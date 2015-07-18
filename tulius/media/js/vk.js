VK.init(function() {
// any of your code here
}
    );
 
    function startConnect() {
        VK.callMethod('showInstallBox');
    }
 
    function requestRights() {
        VK.callMethod('showSettingsBox', 1 + 2); // 1+2 is just an example
    }
 
    function onSettingsChanged(settings) {
        window.location.reload();
    }
 
    $(document).ready( function(){
        VK.addCallback("onApplicationAdded", requestRights);
        VK.addCallback("onSettingsChanged", onSettingsChanged);
    });