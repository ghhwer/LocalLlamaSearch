// ======= SEARCH PAGE LOGIC ==========
var isLoading = false;
var isChatMode = false;
var isLocked = false;
var currentId = null;
//var messages = [
//    {
//        type: 'user',
//        message: 'I am looking for a document on the topic of "Machine Learning"'
//    },
//    {
//        type: 'assistant',
//        message: 'Blablablabla',
//        references: [
//            {
//                uri: 'https://example.com',
//                docName: 'My Example 1',
//                similarity: 0.98
//            },
//            {
//                uri: 'https://example.com',
//                docName: 'My Example 2',
//                similarity: 0.67
//            }
//        ]
//    }
//]
var messages = []

var addUserMessage = function(message) {
    var chatBubble = document.createElement('div');
    chatBubble.classList.add('chat-bubble-user');
    chatBubble.innerHTML = '<div class="no-select">' + message + '</div>';
    document.getElementById('chat-elements').appendChild(chatBubble);
}

var addAssistantMessage = function(message, references) {
    var chatBubble = document.createElement('div');
    chatBubble.classList.add('chat-bubble-assistant');
    chatBubble.innerHTML = '<div class="no-select">' + message + '</div>';
    if (references) {
        var referencesWrapper = document.createElement('div');
        referencesWrapper.classList.add('references-wrapper');
        var referencesText = document.createElement('div');
        referencesText.classList.add('references-text');
        referencesText.innerHTML = 'References';
        referencesWrapper.appendChild(referencesText);
        var referencesDiv = document.createElement('div');
        referencesDiv.classList.add('references');
        for (var i = 0; i < references.length; i++) {
            var reference = references[i];
            var referenceDiv = document.createElement('div');
            referenceDiv.classList.add('reference');
            var uriReference = document.createElement('div');
            uriReference.classList.add('uri-reference');
            uriReference.innerHTML = '<a href="' + reference.uri + '">' + reference.docName + '</a>';
            var similarityReference = document.createElement('div');
            similarityReference.classList.add('similarity-reference');
            similarityReference.innerHTML = reference.similarity;
            referenceDiv.appendChild(uriReference);
            referenceDiv.appendChild(similarityReference);
            referencesDiv.appendChild(referenceDiv);
        }
        referencesWrapper.appendChild(referencesDiv);
        chatBubble.appendChild(referencesWrapper);
    }
    document.getElementById('chat-elements').appendChild(chatBubble);
}
var setIsLoading = function(isLoading) {
    if (isLoading) {
        $("#generating-response").prop("hidden", false);
    }
    else {
        $("#generating-response").prop("hidden", true);
    }
}

var setIsChatMode = function(isChatMode){
    if (isChatMode) {
        $("#chat-content").removeClass("chat-content-expanded");
        $("#chat-content").addClass("chat-content");
        $("#chat-user-input").removeClass("chat-footer-expanded");
        $("#chat-user-input").addClass("chat-footer");
        $("#search-prompt").attr("hidden", true);
    }
    else {
        $("#chat-content").removeClass("chat-content");
        $("#chat-content").addClass("chat-content-expanded");
        $("#chat-user-input").removeClass("chat-footer");
        $("#chat-user-input").addClass("chat-footer-expanded");
        $("#search-prompt").attr("hidden", false);
    }
}

var setIsLocked = function(isLocked) {
    if (isLocked  || isLoading) {
        $("#chat-user-input-text").prop("disabled", true);
        $("#chat-user-send").prop("disabled", true);
    }
    else {
        $("#chat-user-input-text").prop("disabled", false);
        $("#chat-user-send").prop("disabled", false);
    }
}

var updateUI = function() {
    // Clear the chat content
    document.getElementById('chat-elements').innerHTML = '';
    for (var i = 0; i < messages.length; i++) {
        var message = messages[i];
        if (message.type == 'user') {
            addUserMessage(message.message);
        }
        else if (message.type == 'assistant') {
            addAssistantMessage(message.message, message.references);
        }
    }
    setIsLoading(isLoading);
    setIsChatMode(isChatMode);
    setIsLocked(isLocked);
}
updateUI();

// Mocking search response
var callSearchAPI = async function(query) {
    // wait for 5 seconds
    await new Promise(r => setTimeout(r, 5000));
    return {
        llm_response: "Blablablabla blablablabla blablablabla",
        keywords_used: ["Machine Learning", "Deep Learning"],
        search_details: [
            {'uri': "file://example.pdf", 'similarity': 0.98},
            {'uri': "file://example_2.pdf", 'similarity': 0.67}
        ],
        llm_token_count: 100,
        prompt_token_count: 50,
        warn: false,
        queryIndex: 102
    }
}
var callFollowUpAPI = async function(query, queryIndex) {
    // wait for 5 seconds
    await new Promise(r => setTimeout(r, 3000));
    return {
        llm_response: "Blablablabla blablablabla blablablabla blablablabla",
        keywords_used: ["Machine Learning", "Deep Learning"],
        search_details: [
            {'uri': "file://example.pdf", 'similarity': 0.98}
        ],
        llm_token_count: 100,
        prompt_token_count: 50,
        warn: false
    }
}

// Action when search button is clicked or enter is pressed on the input
var onInitialSearch = function(){
    var query = document.getElementById('initial-search-text-input').value;
    query = query.trim();
    if (query == '') {
        showInfoAlert('Please enter a query');
    }

    messages.push({
        type: 'user',
        message: query
    });
    isLoading = true;
    isChatMode = true;
    updateUI();
    // Clear the input
    document.getElementById('initial-search-text-input').value = '';
    // Call the backend to get the response
    callSearchAPI(query).then((response) => {
        isLoading = false;
        currentId = response.queryIndex;
        references = response.search_details.map((reference) => {
            return {
                uri: reference.uri,
                docName: reference.uri.split('/').pop(),
                similarity: reference.similarity
            }
        });
        messages.push({
            type: 'assistant',
            message: response.llm_response,
            references: references
        });
        updateUI();
        if (response.warn) {
            showInfoAlert('Warning: The response may not be accurate due to the size of the context');
        }
        if (messages.length == 4) {
            isLocked = true;
            updateUI();
        }
    });
}
$('#initial-search-btn-input').click(onInitialSearch);
$('#initial-search-text-input').keypress(function(e) {
    if (e.which == 13) {
        onInitialSearch();
    }
});

// Action when send button is clicked or enter is pressed on the input
var onChatUserSend = function(){
    var user_message = document.getElementById('chat-user-input-text').value;
    user_message = user_message.trim();
    if (user_message == '') {
        showInfoAlert('Please enter a message');
    }
    messages.push({
        type: 'user',
        message: user_message
    });
    isLoading = true;
    isChatMode = true;
    updateUI();
    // Clear the input
    document.getElementById('chat-user-input-text').value = '';
    // Call the backend to get the response
    callFollowUpAPI(user_message, currentId).then((response) => {
        isLoading = false;
        references = response.search_details.map((reference) => {
            return {
                uri: reference.uri,
                docName: reference.uri.split('/').pop(),
                similarity: reference.similarity
            }
        });
        messages.push({
            type: 'assistant',
            message: response.llm_response,
            references: references
        });
        updateUI();
        if (response.warn) {
            showInfoAlert('Warning: The response may not be accurate due to the size of the context');
        }
    });
}
$('#chat-user-send').click(onChatUserSend);
$('#chat-user-input-text').keypress(function(e) {
    if (e.which == 13) {
        onChatUserSend();
    }
});
