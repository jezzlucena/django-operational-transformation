// MutationManager is a singleton javascript object
// that handles all the mutation frontend logic
var MutationManager = MutationManager || new function() {
  const self = this;

  // Initialize MutationManager, animations, event handlers, etc.
  this.init = () => {
    self.initVariables();
  };

  // Initialize relevant variables and jquery elements
  this.initVariables = () => {
    self.mutationsUrl = $("#mutations_url").val();

    self.currentConversationId = "1234567890";
    self.currentAuthor = "bob";
    self.currentOrigin = { bob: 0, alice: 0 };
  };

  this.sendMutation = (conversationId, author, data, origin) => {
    console.log(JSON.stringify({ conversationId, author, data, origin }))
    return $.ajax({
      type: "POST",
      data: JSON.stringify({ conversationId, author, data, origin }),
      url: self.mutationsUrl,
      success: function(data) {
        console.log(data);
      }
    });
  };
};