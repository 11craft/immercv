/* Project specific Javascript goes here. */

$(function () {

  $('.cvgraph-prop-editor form').hide();
  $('.cvgraph-prop-editor button[data-property-editor=true]').click(function () {
    var $button = $(this);
    var $form = $button.parent().find('form');
    $button.toggleClass('active');
    $form.toggle('visible');
  });

});
