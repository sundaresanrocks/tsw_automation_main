package com.securecomputing.sftools.harvester.devutils;

/**
 * Created by ANegi_Backup on 8/5/2014.
 */

import java.io.File;

import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.map.ObjectWriter;

import com.securecomputing.sftools.harvester.interfaces.IContentExtractor;
import com.securecomputing.sftools.harvester.util.HarvesterProperties;
/**
 * Harvester content ExtractorDriver.
 * @author anegi1
 *
 */
public final class ContentExtractorDriver {

    /**
     * Default Constructor.
     */
    private ContentExtractorDriver() {

    }

    /**
     * 
     * @param args - cmd line args
     * @throws Exception - throws if any exceptions.
     */
    public static void main(final String[] args) throws Exception {
        int arg = 0;
        String harvesterProprties = args[arg++];
        String className = args[arg++];
        String filename = args[arg++];
        String destination = args[arg++];
        String outputFilename = args[arg++];

        HarvesterProperties.loadProperties(harvesterProprties);

        Class<?> extractorClass = ClassLoader.getSystemClassLoader().loadClass(className);
        IContentExtractor extractorInstance = (IContentExtractor) extractorClass.newInstance();
        extractorInstance.initialize();
        ObjectMapper mapper = new ObjectMapper();
        mapper.enableDefaultTyping(ObjectMapper.DefaultTyping.JAVA_LANG_OBJECT);
        @SuppressWarnings("deprecation")
        ObjectWriter writer = mapper.defaultPrettyPrintingWriter();

        if (null != outputFilename) {
            File file = new File(outputFilename);
            writer.writeValue(file, extractorInstance.getExtractedContent(filename, destination));
        }

    }
}
