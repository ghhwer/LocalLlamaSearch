// ======= SEARCH PAGE LOGIC ==========
var isLoading = false;
var isChatMode = false;
var isLocked = false;
var prompt_history = [];
/**
var messages = [
    {
        "type": "user",
        "message": "What is Buddy's Play Dough?"
    },
    {
        "type": "assistant",
        "message": "**Buddy's Play Dough Recipe**\n\nA classic play dough recipe that's easy to make and fun for kids! This recipe combines flour, water, salt, oil, and cream of tartar to create a smooth and pliable dough. Simply mix all the ingredients together in a saucepan over low heat until the dough pulls away from the sides. Knead it by hand until it's smooth, then store it in an airtight container.\n\n**Ingredients:**\n\n* 1 cup Flour\n* 1 cup Water\n* 1/2 cup Salt\n* 1 tablespoon Oil\n* 2 teaspoons Cream of tartar\n* 4 drops Food coloring\n\n**Instructions:**\n\n1. Mix all ingredients together in a saucepan over low heat.\n2. Cook until the dough pulls away from the sides.\n3. Knead by hand until smooth.\n4. Store in an airtight container.\n\nEnjoy making and playing with Buddy's Play Dough!",
        "references": [
            {
                "uri": "data\\JustForFunRecipes.txt",
                "docName": "data\\JustForFunRecipes.txt",
                "similarity": 0.7993706657138392
            },
            {
                "uri": "data\\JustForFunRecipes.txt",
                "docName": "data\\JustForFunRecipes.txt",
                "similarity": 0.7827904159975079
            },
            {
                "uri": "data\\JustForFunRecipes.txt",
                "docName": "data\\JustForFunRecipes.txt",
                "similarity": 0.7993706657138392
            },
            {
                "uri": "data\\JustForFunRecipes.txt",
                "docName": "data\\JustForFunRecipes.txt",
                "similarity": 0.7827904159975079
            },
            {
                "uri": "data\\JustForFunRecipes.txt",
                "docName": "data\\JustForFunRecipes.txt",
                "similarity": 0.7993706657138392
            }
        ]
    },
    {
        "type": "user",
        "message": "Can I substitute the oil?"
    },
    {
        "type": "assistant",
        "message": "According to the recipe \"Buddy's Play Dough\", the ingredient list includes:\n\n* 1 tablespoon Oil\n\nThis suggests that oil is an essential component of the play dough, and substituting it might affect the texture or consistency of the final product. However, without further information, it's difficult to say for certain whether a substitution would be acceptable.\n\nIf you're looking to substitute the oil, you might consider using another type of liquid ingredient that provides similar properties (e.g., moisture, lubrication). Some options could include:\n\n* Vegetable shortening\n* Coconut oil\n* Glycerin\n\nKeep in mind that substituting the oil might alter the flavor or texture of the play dough. If you do decide to substitute the oil, it's a good idea to start with a small batch and test the results before scaling up.\n\nWould you like me to help with any further questions about this recipe?"
    },
    {
        "type": "user",
        "message": "Just make a guess"
    },
    {
        "type": "assistant",
        "message": "**Guess:** It seems likely that you can substitute the oil in Buddy's Play Dough recipe with another type of oil, as it is used to help bind the ingredients together and add moisture to the dough. Possible substitutes could be vegetable oil, coconut oil, or even baby oil (although this might affect the texture and consistency of the dough). However, keep in mind that using a different type of oil may alter the overall character of the play dough."
    },
    {
        "type": "user",
        "message": "Thank you"
    },
    {
        "type": "assistant",
        "message": "You're welcome! If you have any more questions or need further assistance, feel free to ask. Enjoy making Buddy's Play Dough!"
    }
] **/
var smoothScrollToBottom = function() {
    var chatElements = document.getElementById('chat-elements');
    chatElements.scrollTop = chatElements.scrollHeight;
}
var messages = [];

var render_markdown = function(markdown) {
    var converter = new showdown.Converter();
    return converter.makeHtml(markdown);
}

var addUserMessage = function(message) {
    var chatBubble = document.createElement('div');
    chatBubble.classList.add('chat-bubble-user');
    chatBubble.innerHTML = '<div>' + message + '</div>';
    document.getElementById('chat-elements').appendChild(chatBubble);
}

var addAssistantMessage = function(message, references) {
    var chatBubble = document.createElement('div');
    chatBubble.classList.add('chat-bubble-assistant');
    message_mkdown = render_markdown(message);
    chatBubble.innerHTML = '<div>' + message_mkdown + '</div>';
    if (references) {
        var referencesWrapper = document.createElement('div');
        referencesWrapper.classList.add('references-wrapper');
        var referencesText = document.createElement('div');
        referencesText.classList.add('references-text');
        referencesText.innerHTML = 'References';
        referencesWrapper.appendChild(referencesText);
        var referencesDiv = document.createElement('div');
        referencesDiv.classList.add('references');
        let referencesDedupe = {};
        // Group by references with the same uri and get the max similarity
        references.forEach((reference) => {
            if (!referencesDedupe[reference.uri] || referencesDedupe[reference.uri].similarity < reference.similarity) {
                referencesDedupe[reference.uri] = reference;
            }
        });
        
        for (let uri in referencesDedupe) {
            var reference = referencesDedupe[uri];
            var referenceDiv = document.createElement('div');
            referenceDiv.classList.add('reference');
            var uriReference = document.createElement('div');
            uriReference.classList.add('uri-reference');
            var normalizedDocName = reference.docName.split('\\').pop().split('/').pop();
            var url = `http://${API_URI}/api/files/${normalizedDocName}`;
            uriReference.innerHTML = `<a href="${url}" target="_blank">${normalizedDocName}</a>`;
            var similarityReference = document.createElement('div');
            similarityReference.classList.add('similarity-reference');
            similarityReference.innerHTML = reference.similarity.toFixed(2);
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
        $('#chat-header').removeClass("hide");
        $("#chat-content").removeClass("chat-content-expanded");
        $("#chat-content").addClass("chat-content");
        $("#chat-user-input").removeClass("chat-footer-expanded");
        $("#chat-user-input").addClass("chat-footer");
        $("#search-prompt").attr("hidden", true);
    }
    else {
        $('#chat-header').addClass("hide");
        $("#chat-content").removeClass("chat-content");
        $("#chat-content").addClass("chat-content-expanded");
        $("#chat-user-input").removeClass("chat-footer");
        $("#chat-user-input").addClass("chat-footer-expanded");
        $("#search-prompt").prop("hidden", false);
    }
}

var setIsLocked = function(isLocked) {
    if (isLocked  || isLoading) {
        $("#chat-user-input-text").prop("disabled", true);
        $("#chat-user-send").prop("disabled", true);
        if (isLoading) {
            $("#reset-chat").prop("disabled", true);
        }
    }
    else {
        $("#chat-user-input-text").prop("disabled", false);
        $("#chat-user-send").prop("disabled", false);
        $("#reset-chat").prop("disabled", false);
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
    // Set hard limit of 4 messages
    if (messages.length == 8) {
        isLocked = true;
    }
    setIsLoading(isLoading);
    setIsChatMode(isChatMode);
    setIsLocked(isLocked);
    smoothScrollToBottom();
}
updateUI();

// Mocking search response
var callSearchAPI = async function(query) {
    // wait for 5 seconds
    let url = 'http://' + API_URI + '/api/query';
    let response = await fetch(url, {
        method: 'POST',
        body: JSON.stringify({query: query}),
        headers: {
            'Content-Type': 'application/json'
        }
    });
    let response_json = await response.json();
    prompt_history = response_json.prompt_history;
    return response_json;
}
var callFollowUpAPI = async function(query) {
    // wait for 5 seconds
    let url = 'http://' + API_URI + '/api/query/followup';
    let response = await fetch(url, {
        method: 'POST',
        body: JSON.stringify({query: query, prompt_history: prompt_history}),
        headers: {
            'Content-Type': 'application/json'
        }
    });
    let response_json = await response.json();
    prompt_history = response_json.prompt_history;
    return response_json;
}

// Action when reset button is clicked
var onResetChat = function() {
    messages = [];
    prompt_history = [];
    isLoading = false;
    isChatMode = false;
    isLocked = false;
    updateUI();
}
$('#reset-chat').click(onResetChat);

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
    callFollowUpAPI(user_message).then((response) => {
        isLoading = false;
        messages.push({
            type: 'assistant',
            message: response.llm_response,
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
