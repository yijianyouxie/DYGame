mergeInto(LibraryManager.library,{
	unityCallJs:function(msg){
		UNBridgeCore.handleMsgFromUnity(Pointer_stringify(msg));
	},
	unityCallJsSync:function(msg){
		var result = UNBridgeCore.handleMsgFromUnitySync(Pointer_stringify(msg));
	    var bufferSize = lengthBytesUTF8(result) + 1;
	    var buffer = _malloc(bufferSize);
	    stringToUTF8(result, buffer, bufferSize);
	    return buffer;
	},
	h5HasAPI:function(apiName){
		return UNBridge.h5HasAPI(Pointer_stringify(apiName));
	},
	unityMixCallJs:function(msg){
		var result = UNBridgeCore.onUnityMixCall(Pointer_stringify(msg));
	    var bufferSize = lengthBytesUTF8(result) + 1;
	    var buffer = _malloc(bufferSize);
	    stringToUTF8(result, buffer, bufferSize);
	    return buffer;
	}
	
});
