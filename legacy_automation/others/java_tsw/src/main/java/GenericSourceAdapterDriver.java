/**
 * 
 * McAfee GenericSourceAdapter Class
 * 
 * Copyright (c) 2011, McAfee Corporation. All rights reserved.
 * 
 * $Id: $
 * 
 */
package com.securecomputing.sftools.harvester.devutils;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.io.FilenameUtils;
import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.map.ObjectWriter;

import com.mcafee.tsw.catserver.CatserverClient;
import com.securecomputing.sftools.harvester.exception.HarvesterGeneralException;
import com.securecomputing.sftools.harvester.fact.Fact;
import com.securecomputing.sftools.harvester.interfaces.IContentExtractor;
import com.securecomputing.sftools.harvester.interfaces.IContentParser;
import com.securecomputing.sftools.harvester.interfaces.IContentProvider;
import com.securecomputing.sftools.harvester.interfaces.IPreprocessor;
import com.securecomputing.sftools.harvester.sanityCheck.DmsSanityCheck;
import com.securecomputing.sftools.harvester.util.HarvesterProperties;
import com.securecomputing.sftools.harvester.util.HarvesterUtils;
/**
 * Comment here.
 * 
 * @author spelzer
 * 
 */

public class GenericSourceAdapterDriver {
    /** Create IContentProvider object. */
    private IContentProvider contentProvider = null;
    /** Create IContentExtractor object. */
    private IContentExtractor contentExtractor = null;
    /** Create IContentParser object. */
    private IContentParser contentParser = null;
    /** Create an IPreprocessor list. */
    private ArrayList<IPreprocessor> preprocessors = null;
    /** Count of expected number of IPreprocessor objects. */
    private int preprocessorCount = 0;

    /**
     * Does any initialization needed. Example loads ContentProvider and ContentParser
     * 
     * @return TRUE if the initilizaiton succeeds
     * @throws HarvesterGeneralException A harvester general exception
     */
    public final boolean initialize() throws HarvesterGeneralException {
        String providerClass = HarvesterProperties.getProperty("ContentProvider.className");
        String extractorClass = HarvesterProperties.getProperty("ContentExtractor.className");
        String parserClass = HarvesterProperties.getProperty("ContentParser.className");
        if (null != providerClass) {
            contentProvider = (IContentProvider) HarvesterUtils.loadClass(providerClass);
            if (null == contentProvider) {
                throw new HarvesterGeneralException("There was a problem loading the content provider.  "
                        + "Please check the config file and verify the classname is correct: " + providerClass);
            }
            contentProvider.initialize();
        }

        if (null != extractorClass) {
            contentExtractor = (IContentExtractor) HarvesterUtils.loadClass(extractorClass);
            if (null == contentExtractor) {
                throw new HarvesterGeneralException("There was a problem loading the content extractor.  "
                        + "Please check the config file and verify the classname is correct: " + extractorClass);
            }
            contentExtractor.initialize();
        }

        contentParser = (IContentParser) HarvesterUtils.loadClass(parserClass);
        if (null == contentParser) {
            throw new HarvesterGeneralException("There was a problem loading the content parser.  "
                    + "Please check the config file and verify the classname is correct: "
                    + HarvesterProperties.getProperty("ContentParser.className"));
        }
        contentParser.baseInitialize();

        // Initialize the preprocessors list
        String preprocessorCountStr = HarvesterProperties.getProperty("Preprocessor.count");

        // Check to see if we have any preprocessors
        if (null != preprocessorCountStr) {
            preprocessorCount = Integer.parseInt(preprocessorCountStr);

            preprocessors = new ArrayList<IPreprocessor>();
            for (int i = 1; i <= preprocessorCount; i++) {
                String preprocessorClassName = HarvesterProperties.getProperty("Preprocessor." + i + ".className");
                if (null == preprocessorClassName) {
                    throw new HarvesterGeneralException("Unable to find property: Preprocessor." + i + ".className");
                }
                IPreprocessor preprocessor = (IPreprocessor) HarvesterUtils.loadClass(preprocessorClassName);

                if (null == preprocessor) {
                    throw new HarvesterGeneralException("Unable to load preprocessor class for Preprocessor." + i
                            + ".className: " + preprocessorClassName);
                } else {
                    preprocessor.initialize();
                    preprocessors.add(preprocessor);
                }
            }
        }

        return true;
    }

    /**
     * Parses the content of the source file.
     * 
     * @param file The source file to be parsed
     * @throws HarvesterGeneralException A harvester general exception
     * @return parseContent Return the parsed content of the source file
     */
    public final LinkedHashMap<String, ArrayList<Fact>> parseFile(final File file) throws HarvesterGeneralException {
        String parseFile = file.getAbsolutePath();

        if (0 != preprocessorCount) {
            File outputFile = null;
            try {
                outputFile = File.createTempFile(file.getName(), ".tmp", new File("/tmp"));
            } catch (IOException e) {
                throw new HarvesterGeneralException("Unable to get temporary file: " + e.getMessage());
            }

            FileInputStream fis = null;
            try {
                fis = new FileInputStream(file);
            } catch (FileNotFoundException e) {
                throw new HarvesterGeneralException("Unable to open input file: " + e.getMessage());
            }

            FileOutputStream fos = null;
            try {
                fos = new FileOutputStream(outputFile);
            } catch (FileNotFoundException e) {
                throw new HarvesterGeneralException("Unable to open output file: " + e.getMessage());
            }

            BufferedReader in = new BufferedReader(new InputStreamReader(fis));

            StringWriter sw = new StringWriter();
            BufferedWriter out = new BufferedWriter(sw);
            StringBuffer sb = sw.getBuffer();

            // Run all of the preprocessors on the data
            for (int i = 0; i < (preprocessorCount - 1); i++) {
                preprocessors.get(i).processContents(in, out);
                try {
                    out.flush();
                } catch (IOException e) {
                    throw new HarvesterGeneralException("Flushing output buffer failed: " + e.getMessage());
                }

                in = new BufferedReader(new StringReader(sb.toString()));
                sb.setLength(0);
            }
            out = new BufferedWriter(new OutputStreamWriter(fos));
            preprocessors.get(preprocessorCount - 1).processContents(in, out);
            try {
                out.close();
            } catch (IOException e) {
                throw new HarvesterGeneralException("Closing output file failed: " + e.getMessage());
            }
            parseFile = outputFile.getAbsolutePath();
        }

        contentParser.parseContent(parseFile);

        return contentParser.getTasks();
    }

    /**
     * Returns the list of facts that would have been stored in the database.
     * 
     * @return List of prop/value pairs
     * @throws HarvesterGeneralException Harvester exceptions
     */
    public final Map<String, String> getPersistedFactProperties() throws HarvesterGeneralException {
        return contentParser.getTrackedFactProperties();
    }

    /**
     * Does any needed clean up. Clean up should be done in the opposite order as initialize.
     * 
     * @throws HarvesterGeneralException A harvester general exception
     */
    public final void cleanup() throws HarvesterGeneralException {
        if (null != contentProvider) {
            contentProvider.cleanup();
        }

        if (null != contentExtractor) {
            contentExtractor.cleanup();
        }

        contentParser.baseCleanup();

        for (int i = 0; i < preprocessorCount; i++) {
            IPreprocessor preprocessor = preprocessors.get(i);
            preprocessor.cleanup();
        }

    }

    /**
     * Get the list of files to process.
     * 
     * @return List of filenames
     * @throws HarvesterGeneralException - Exceptions
     */
    public final List<String> getFileList() throws HarvesterGeneralException {
        List<String> filenameList = null;
        if (null != contentProvider) {

            // Get a list of file names
            if (null != contentExtractor) {
                filenameList = contentProvider.getContent();
                filenameList = contentExtractor.getExtractedContentBase(filenameList);
            } else {
                filenameList = contentProvider.getContent();
            }

        }
        return filenameList;
    }

    /**
     * Main entry point (for testing).
     * 
     * @param args Command line arguments
     * @throws HarvesterGeneralException - throws if any
     * @throws IOException - throws if any
     */
    public static void main(final String[] args) throws HarvesterGeneralException, IOException {
        ArrayList<String> filenameList = null;
        CatserverClient catserver = new CatserverClient();
        DmsSanityCheck dmsSanityCheck = new DmsSanityCheck();
        GenericSourceAdapterDriver driver = new GenericSourceAdapterDriver();
        HarvesterProperties.loadProperties(args[0]);
        driver.initialize();
        dmsSanityCheck.initialize();

        if (1 < args.length) {
            filenameList = new ArrayList<String>();
            for (int i = 1; i < args.length; i++) {
                filenameList.add(args[i]);
            }
        } else {
            filenameList = (ArrayList<String>) driver.getFileList();
        }

        ObjectMapper mapper = new ObjectMapper();
        mapper.enableDefaultTyping(ObjectMapper.DefaultTyping.JAVA_LANG_OBJECT);
        @SuppressWarnings("deprecation")
        ObjectWriter writer = mapper.defaultPrettyPrintingWriter();
        File file = null;
        int fileCounter = 0;
        for (String filename : filenameList) {
            LinkedHashMap<String, ArrayList<Fact>> taskList = driver.parseFile(new File(filename));
            System.out.println(writer.writeValueAsString(taskList));

            //write to file
            String outputFilename = "out-" + fileCounter++ + "-" + FilenameUtils.getName(filename) + ".parsed";
            System.out.println("\nparsed file name: " + outputFilename);
            file = new File(outputFilename);
            if (null != file) {
                writer.writeValue(file, taskList);
            }
            file = null;

            for (Map.Entry<String, ArrayList<Fact>> entry : taskList.entrySet()) {
                int categoryCount = 0;

                try {
                    ArrayList<String> categories = catserver.getCategories(entry.getKey());

                    System.out.print(entry.getKey());

                    if (dmsSanityCheck.matches(entry.getKey())) {
                        System.out.print("\tdms_sanity_match=true");
                    } else {
                        System.out.print("\tdms_sanity_match=false");
                    }

                    System.out.print("\tcategoryFact=");

                    for (String category : categories) {
                        if (categoryCount == 0) {
                            System.out.print(category);
                        } else {
                            System.out.print("," + category);
                        }
                    }

                    System.out.print("\n");
                    // System.out.println(entry.getKey() + "\t" + entry.getValue().toString());
                } catch (Exception e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
            }

        }
        Map<String, String> props = driver.getPersistedFactProperties();
        for (Map.Entry<String, String> entry : props.entrySet()) {
            System.out.println("'" + entry.getKey() + "' => '" + entry.getValue() + "'");
        }

        driver.cleanup();
    }
}
