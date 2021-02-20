// Initialize all managers when the DOM is fully rendered
$(document).ready(() => {
  MutationManager.init();
  ConversationManager.init();
});