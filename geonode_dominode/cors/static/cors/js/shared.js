let dispatcher;
let Request;
let csrfmiddlewaretoken;

String.prototype.replaceAll = function (search, replacement) {
    let target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
}

String.prototype.capitalize = function () {
    let target = this;
    return target.charAt(0).toUpperCase() + target.slice(1);
}

function beforeAjaxSend(xhr) {
    xhr.setRequestHeader('X-CSRFToken', token);
}

/**
 * Clone object
 *
 * @param obj
 * @returns {*}
 */
function cloneObject(obj) {
    if (obj === null || typeof obj !== 'object') {
        return obj;
    }

    let temp = obj.constructor(); // give temp the original obj's constructor
    for (let key in obj) {
        temp[key] = cloneObject(obj[key]);
    }

    return temp;
}

function capitalize(string) {
    //check if it is already has upper case
    string = string.replaceAll('_', ' ')
    if (/[A-Z]/.test(string)) {
        return string;
    }
    return string.charAt(0).toUpperCase() + string.slice(1);
}