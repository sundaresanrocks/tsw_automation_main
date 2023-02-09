package com.securecomputing.sftools.harvester.devutils;

import java.io.File;
import java.util.ArrayList;
import java.util.LinkedHashMap;

import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.map.ObjectWriter;

import com.securecomputing.sftools.harvester.fact.Fact;
import com.securecomputing.sftools.harvester.interfaces.IContentParser;
import com.securecomputing.sftools.harvester.util.HarvesterProperties;
/**
 * Created by mfinger on 2/24/14.
 */
public final class ContentParserDriver {

    /** Private constructor. */
    private ContentParserDriver() {

    }

    /**
     * Main execution routine.
     *
     * @param args Command line arguments
     * @throws Exception Any errors
     */
    public static void main(final String[] args) throws Exception {
        System.out.println(args.length);
        System.out.println("Args: harvester_properties class_name input_file_name [output_file_name]");
        int arg = 0;
        String harvesterProprties = args[arg++];
        String className = args[arg++];
        String filename = args[arg++];
        String outputFilename = null;
        if (args.length > 2) {
            outputFilename = args[arg++];
        }

        HarvesterProperties.loadProperties(harvesterProprties);

        Class<?> parserClass = ClassLoader.getSystemClassLoader().loadClass(className);
        IContentParser parserInstance = (IContentParser) parserClass.newInstance();
        parserInstance.baseInitialize();
        parserInstance.parseContent(filename);
        LinkedHashMap<String, ArrayList<Fact>> taskList;
        taskList = parserInstance.getTasks();

        ObjectMapper mapper = new ObjectMapper();
        mapper.enableDefaultTyping(ObjectMapper.DefaultTyping.JAVA_LANG_OBJECT);
        @SuppressWarnings("deprecation")
        ObjectWriter writer = mapper.defaultPrettyPrintingWriter();
        System.out.println(writer.writeValueAsString(taskList));
        if (null != outputFilename) {
            File file = new File(outputFilename);
            writer.writeValue(file, taskList);
        }
    }
}
