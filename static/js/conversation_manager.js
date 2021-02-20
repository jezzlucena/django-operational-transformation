// ConversationManager is a singleton javascript object
// that handles all the conversation frontend logic
var ConversationManager = ConversationManager || new function() {
  const self = this;

  // Initialize ConversationManager, animations, event handlers, etc.
  this.init = () => {
    self.initVariables();
    self.retrieveConversations();
    $(".conversations-table").fadeOut(500);

    $(".update-icon").click(() => {
      $(".update-icon, .conversations-table").fadeOut(500, () => {
        $("#conversationsContainer").html("");
        self.retrieveConversations();
        self.markedForUpdate = true;
        $(".spinner-border").fadeIn(500);
      });
    })
  };

  // Initialize relevant variables and jquery elements
  this.initVariables = () => {
    self.conversationsUrl = $("#conversations_url").val();
    self.mutationsUrl = $("#mutations_url").val();
    self.conversationsDict = {};
    self.markedForUpdate = true;

    self.currentConversationId = "1234567890";
    self.currentAuthor = "bob";
    self.currentOrigin = { bob: 0, alice: 0 };
  };

  // Retrieve all conversations from the database
  this.retrieveConversations = () => {
    $.ajax({
      type: "GET",
      url: self.conversationsUrl,
      success: function(data) {
        $(".spinner-border").fadeOut(500, () => {
          $(".update-icon").fadeIn(500);
        });

        if (!data.conversations || data.conversations.length == 0) {
          $(".conversations-table").fadeOut(500);
          clearTimeout(self.updateTimeout);
          self.updateTimeout = undefined;
        } else {
          self.conversationsDict = Object.assign({}, ...data.conversations.map((x) => ({[x.id]: x})));
          if (self.markedForUpdate) {
            self.renderConversations(data.conversations);
          }
        }
      }
    }).then(() => {
      self.markedForUpdate = false;
      self.updateTimeout = setTimeout(() => {
        if (!!self.currentConversationId) {
          self.retrieveConversations();
          self.renderConversation(self.currentConversationId);
        }
      }, 1000);
    });
  };

  // Render all conversations passed in a given array
  this.renderConversations = conversations => {
    const conversationTemplateElem = $("#conversationTemplateElem");

    // Iterate through all conversation creating clones of the conversation template
    if (conversations && conversations.length > 0) {
      conversations.forEach(conversation => {
        const newConversation = $(conversationTemplateElem).clone();
        newConversation.find(".id").text(conversation.id);
        newConversation.find(".text").text(conversation.text);

        // If a last mutation is present, format the data into a pretty string
        // show in a <pre/> html element
        if (conversation.lastMutation) {
          self.currentOrigin = conversation.lastMutation.origin;

          let typeOrLengthCopy = "";
          if (conversation.lastMutation.data.type == "insert") {
            typeOrLengthCopy = `inserted "${conversation.lastMutation.data.text}" to`
          } else if (conversation.lastMutation.data.type == "delete") {
            typeOrLengthCopy = `deleted ${conversation.lastMutation.data.length} characters from`
          }

          let authors = Object.keys(conversation.lastMutation.origin);
          const originArr = [];
          authors.forEach(author => {
            originArr.push(`"${author}": ${conversation.lastMutation.origin[author]}`)
          })
          newConversation.find(".lastMutation pre")
            .text(`${conversation.lastMutation.author} ${typeOrLengthCopy} index ${conversation.lastMutation.data.index}\norigin = {${originArr.join(", ")}}`);
        }

        // Attach click handlers for opening the lightbox with updating conversation
        newConversation.find("i.open").click(function() {
          self.currentConversationId = conversation.id;
          const currentConversationElem = $("<pre class='conversationModal'/>");
          currentConversationElem.attr("data-conversation-id", conversation.id);

          $.featherlight(currentConversationElem, {
            afterClose: () => {
              self.currentConversationId = undefined;
            }
          });

          self.renderConversation();
        });

        // Show favorites depending on cookies
        const isStarred = CookieManager.readCookie(conversation.id);
        newConversation.find("i.star").toggleClass("starred", !!isStarred)
          .attr("data-conversation-id", conversation.id)
          .click(function() {
            $(this).toggleClass("starred");
            const conversationId = $(this).attr("data-conversation-id");
            if ($(this).hasClass("starred")) {
              CookieManager.setCookie(conversationId, "true");
            } else {
              CookieManager.eraseCookie(conversationId);
            }
          });

        // Attach click handlers to the delete button
        newConversation.find("i.delete").click(() => {
          self.deleteConversation(conversation.id)
            .then(() => {
              if ($("#conversationTemplateElem:not(.d-none)").length == 0) {
                $(".conversations-table").fadeOut(500);
              }
              newConversation.fadeOut(500, () => {
                newConversation.remove();
              });
            });
        });

        newConversation.appendTo($("#conversationsContainer"));
        newConversation.removeClass("d-none");
      });

      $(".conversations-table").fadeIn(500);
    } else {
      // If no conversations were passed, fade out the entire table
      $(".conversations-table").fadeOut(500);
    }
  };

  // Render the currently selected conversation in the lightbox
  this.renderConversation = () => {
    $(".featherlight-content pre").html(
      `Conversation Id: ${self.currentConversationId}\n\n${self.conversationsDict[self.currentConversationId].text}`);
  };

  // Delete a conversation based on a certain conversation id
  this.deleteConversation = (conversationId) => {
    return $.ajax({
      type: "DELETE",
      data: JSON.stringify({ conversationId }),
      url: self.conversationsUrl,
      success: function(data) {
        console.log(data);
      }
    });
  };
};