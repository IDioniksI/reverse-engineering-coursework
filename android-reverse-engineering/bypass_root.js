console.log("Starting bypass script...");

// bypass 'goodbye()'
try {
    Interceptor.attach(Module.findExportByName("libc.so", "strstr"), {
        onEnter: function (args) {
            // strstr(const char *haystack, const char *needle)
            this.haystack_str = args[0].readCString();
            this.needle_str   = args[1].readCString();
            this.frida_detected = false;

            if (this.haystack_str && (this.haystack_str.includes("frida") || this.haystack_str.includes("xposed"))) {
                this.frida_detected = true;
            }

            if (this.needle_str && (this.needle_str.includes("frida") || this.needle_str.includes("xposed"))) {
                this.frida_detected = true;
            }
        },
        onLeave: function (retval) {
            if (this.frida_detected) {
                console.log("[Native] 'strstr' check for 'frida'/'xposed' detected. Bypassed!");
                retval.replace(0);
            }
        }
    });
    console.log("[Native] 'strstr' hook is in place.");
} catch (error) {
    console.error("[Native] Failed to hook 'strstr':", error.message);
}


// bypass Root/Debug
Java.perform(function () {
    console.log("[Java] VM is ready. Placing Java hooks...");

    try {
        var sys = Java.use("java.lang.System");
        sys.exit.overload("int").implementation = function(var_0) {
            console.log("[Java] System.exit(" + var_0 + ") CALLED! ... Bypassing!");
        };
        console.log("[Java] 'System.exit' hook installed.");
    } catch (e) {
        console.error("[Java] Failed to hook System.exit:", e.message);
    }

    try {
        const RootDetection = Java.use("sg.vantagepoint.util.RootDetection");
        RootDetection.checkRoot1.implementation = function() { return false; };
        RootDetection.checkRoot2.implementation = function() { return false; };
        RootDetection.checkRoot3.implementation = function() { return false; };
        console.log("[Java] 'RootDetection' hooks installed.");
    } catch (e) {

    }

    try {
        const Debug = Java.use("android.os.Debug");
        Debug.isDebuggerConnected.implementation = function() {
            return false;
        };
        console.log("[Java] 'Debug.isDebuggerConnected' hook installed.");
    } catch (e) {

    }

    console.log("[Java] All Java hooks are installed.");
});
