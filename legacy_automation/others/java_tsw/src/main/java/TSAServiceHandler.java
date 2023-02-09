import httpd.NanoHTTPD;
import httpd.NanoHTTPD.Response;
import com.mcafee.tsw.util.NormalizeUrl;
import com.securecomputing.sftools.jnilib.UrlCanonicalizeImpl;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.codec.digest.DigestUtils;
import org.json.simple.JSONObject;

import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;


import java.lang.UnsatisfiedLinkError;

/**
 * Created by manoj on 2/28/14.
 */

public class TSAServiceHandler {
    private String lastErrorResponse;

    public NanoHTTPD.Response serve(NanoHTTPD.IHTTPSession session) {
        String uri = session.getUri();
         if (uri.equalsIgnoreCase("/canon") || uri.toLowerCase().startsWith("/canon/")){
            return getCanonServiceResponse(uri.substring(6));
        }
        else if (uri.equals("/repper") || uri.startsWith("/repper/")){
            return getRepperServiceResponse(uri);
        }
        else if (uri.equals("/catserver") || uri.startsWith("/catserver/")){
            return getCatServiceResponse(uri);
        }
        return Responses.wrapUnknownServiceResponse("Unknown request!");
    }

    private Response getCatServiceResponse(String uri) {
        return Responses.wrapUnknownServiceResponse("Not implemented");
    }
    private Response getRepperServiceResponse(String uri) {
        return Responses.wrapUnknownServiceResponse("Not implemented");
    }


    private Response getCanonServiceResponse(String canon_request) {
        String original_url;
        if (null == canon_request || canon_request.isEmpty()){
            return Responses.wrapBadResponse("canon: Empty request");
        }

        if (canon_request.toLowerCase().startsWith("/b64ue/")){
            original_url = decodeB64URLEncodedUrl(canon_request.substring(7));
        }
        else if (canon_request.toLowerCase().startsWith("/b64/")){
            original_url = decodeB64(canon_request.substring(5));
        }
        else{
            return Responses.wrapUnknownServiceResponse("canon: supports b64ue request type - format /canon/b64ue/<encodeded url> <where encoded url> = base64encode(urlencode(<url>))\n Example: google.com should be requested as /canon/b64ue/Z29vZ2xlLmNvbSUwRCUwQQ==");
        }


        if (null == original_url){
            return Responses.wrapBadResponse(this.lastErrorResponse);
        }

        String return_json;
        try {
            return Responses.wrapSuccessResponse(getCanonJSONObject(original_url));
        } catch (java.lang.IllegalArgumentException e){
            return Responses.wrapBadResponse(e.toString() + e.getMessage());
        } catch (UnsatisfiedLinkError e) {
            return Responses.wrapBadResponse(e.toString() + e.getMessage());
        } catch (java.lang.NoClassDefFoundError e){
            return Responses.wrapBadResponse("Unexpected Error:" + e.toString());
        } catch (Exception e) {
            return Responses.wrapBadResponse("Unexpected Error:" + e.toString());
        }
    }

    private String decodeB64URLEncodedUrl(String b64UEUrlString){
        String url = null;
        try{
            url = URLDecoder.decode(new String(decodeB64(b64UEUrlString)), "UTF-8").trim();
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
            this.lastErrorResponse = "URLDecoder.decode: Unable to decode request from URL Encoded data";
        } catch (Exception e){
            e.printStackTrace();
            this.lastErrorResponse = "decodeBase64URLEncodedUrl: Unable to decode request";
        }
        return url;
    }

    private String decodeB64(String b64String){
        byte[] decodedBase64 = null;
        try{
            decodedBase64 = Base64.decodeBase64(b64String.trim());
        }catch (Exception e){
            e.printStackTrace();
            this.lastErrorResponse = "decodeBase64: Unable to decode request";
        }
        return (null == decodedBase64) ? new String(""): new String(decodedBase64);
    }

    private JSONObject getCanonJSONObject(String urlIn) {

        String normaliedUrl;
        NormalizeUrl normalizer = new NormalizeUrl();
        normaliedUrl = normalizer.getStandardUrlFormat(urlIn);
        UrlCanonicalizeImpl urlCanon = new UrlCanonicalizeImpl(normaliedUrl);
        JSONObject data = new JSONObject();
        data.put("original-url", urlIn);
        urlCanon.getBrowserCanonUrl();      //not used?
        urlCanon.getBrowserCanonUrlRemoveProto();   //not used?
        data.put("cl-hash", urlCanon.getCanonAndHash());
        String canonUrl = urlCanon.getCanonUrl();

        data.put("canon-url", canonUrl);
        data.put("db-hash", urlCanon.getDbHash());
        data.put("sha256", org.apache.commons.codec.digest.DigestUtils.sha256Hex(canonUrl));
        data.put("md5", urlCanon.getMD5Hash());

        //todo: compute sha256 from the url
        //todo: extract domain name from the url
        return data;
    }


}
