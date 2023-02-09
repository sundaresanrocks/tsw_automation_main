import httpd.NanoHTTPD;
import org.json.simple.JSONObject;

/**
 * Created by manoj on 3/12/14.
 */
public class Responses {
    public static NanoHTTPD.Response wrapSuccessResponse(Object dataObject){
        JSONObject jsonObject = new JSONObject();
        jsonObject.put("status", "success");
        jsonObject.put("data", dataObject);
        return new NanoHTTPD.Response(NanoHTTPD.Response.Status.OK, NanoHTTPD.MIME_PLAINTEXT, jsonObject.toJSONString());
    }

    public static NanoHTTPD.Response wrapBadResponse(Object dataObject){
        JSONObject jsonObject = new JSONObject();
        jsonObject.put("status", "fail");
        jsonObject.put("data", dataObject);
        return new NanoHTTPD.Response(NanoHTTPD.Response.Status.BAD_REQUEST, NanoHTTPD.MIME_PLAINTEXT, jsonObject.toJSONString());
    }

    public static NanoHTTPD.Response wrapUnknownServiceResponse(Object dataObject){
        JSONObject jsonObject = new JSONObject();
        jsonObject.put("status", "fail");
        jsonObject.put("data", dataObject);
        return new NanoHTTPD.Response(NanoHTTPD.Response.Status.NOT_FOUND, NanoHTTPD.MIME_PLAINTEXT, jsonObject.toJSONString());
    }
}
