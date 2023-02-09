/**
 * Created by manoj on 5/22/14.
 */

import com.mcafee.tsw.util.NormalizeUrl;
import com.securecomputing.sftools.jnilib.UrlCanonicalizeImpl;
import sun.nio.cs.StreamDecoder;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.ListIterator;
//import org.apache.commons.codec.*;
import java.security.MessageDigest;

public class CanonFile {
    public static String canonUrlCsv(String UrlIn) throws Exception{
        String csv_line;
        String normaliedUrl;

        NormalizeUrl normalizer = new NormalizeUrl();
        normaliedUrl = normalizer.getStandardUrlFormat(UrlIn);
        UrlCanonicalizeImpl urlCanon = new UrlCanonicalizeImpl(normaliedUrl);
        String canonUrl = urlCanon.getCanonUrl();
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        md.update(canonUrl.getBytes());
        byte byteData[] = md.digest();

        StringBuffer sha = new StringBuffer();
        for (int i = 0; i < byteData.length; i++) {
            sha.append(Integer.toString((byteData[i] & 0xff) + 0x100, 16).substring(1));
        }

        csv_line = "\"" + urlCanon.getMD5Hash() + "\"";
        csv_line += ",\"" + sha.toString() + "\"";
        csv_line += ",\"" + urlCanon.getDbHash() + "\"";
        csv_line += ",\"" + urlCanon.getCanonAndHash() + "\"";
        csv_line += ",\"" + canonUrl + "\"";
        csv_line += ",\"" + UrlIn + "\"";
        return csv_line;
    }

    public static void main(String args[]) throws Exception{
        List<String> list = new ArrayList<String>();
        List<String> final_list = new ArrayList<String>();
        File in_file = new File(args[0]);
        File out_file = new File(args[1]);
        Integer rank = new Integer(Integer.parseInt(args[2]));
        BufferedReader reader = null;

        try {
            reader = new BufferedReader(new FileReader(in_file));
            String text = null;

            while (((text = reader.readLine()) != null)) {
                if (!(text.trim().startsWith("#"))){
                    list.add(text);
                }
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {
                if (reader != null) {
                    reader.close();
                }
            } catch (IOException e) {
            }
        }

        BufferedWriter out = new BufferedWriter(new FileWriter(out_file));
        out.write("md5,sha-256,db-hash,cl-hash,canon-url,original-url,error\r\n");
        for (ListIterator<String> iter = list.listIterator(); iter.hasNext(); ) {
            String urlIn = iter.next();
            String csvOut;
            try{
                csvOut = canonUrlCsv(urlIn);
            } catch (Exception e){
                csvOut = ",,,,,," + e.getMessage();
            }
            out.write(csvOut + ",\n");
//            final_list.add(csvOut);
            rank += 1;
        }
//print out the list
            out.close();
//            System.out.println(final_list);
    }
}
