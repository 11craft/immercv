/* Project specific Javascript goes here. */

$(function () {

  var $editors = $('.cvgraph-editor');

  $editors.find('form').hide();
  $editors.find('button[data-property-editor=true]').click(function () {
    var $button = $(this);
    var $form = $button.parent().find('form');
    $button.toggleClass('active');
    $form.toggle(100);
    if ($form.is(':visible')) {
      $form.find('input[type=text],textarea').first().focus();
    }
  });

  $('#preview-toggle').click(function () {
    var $button = $(this);
    $button.toggleClass('active');
    $editors.toggle(100);
  });

});
