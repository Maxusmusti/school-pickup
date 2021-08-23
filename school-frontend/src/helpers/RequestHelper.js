const makePOST = (route, body, headers, onCompletion, forceResponse=false) => {
    let targetURL = route
    fetch(targetURL, {
        method: 'POST',
        headers: headers,
        body: body
    })
    .then((response) => {
        if(response.ok) {
            return response.json();
        } else {
            return forceResponse ? response.json() : {}
        }
    })
    .then((responseData) => {
        onCompletion(responseData)
    })
}

const makeGET = (route, onCompletion, forceResponse) => {
    fetch(route)
    .then(response => {
        if(response.ok) {
            return response.json();
        } else {
            return forceResponse ? response.json() : {}
        }
    })
    .then(data => onCompletion(data));
}

module.exports = {
    makePOST,
    makeGET
};