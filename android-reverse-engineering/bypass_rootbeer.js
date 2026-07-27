Java.perform(function () {
    var RootBeer = Java.use("com.scottyab.rootbeer.RootBeer");
    RootBeer.checkForDangerousProps.implementation = function () {
        return false;
    };
    RootBeer.checkForSuBinary.implementation = function () {
        return false;
    };
});

