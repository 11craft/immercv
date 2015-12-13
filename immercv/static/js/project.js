/* Project specific Javascript goes here. */

$(function () {

  var $editors = $('.cvgraph-editor');
  var $previewToggle = $('#preview-toggle');

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

  $previewToggle.click(function () {
    $editors.toggle(100);
    if ($previewToggle.prop('checked') == true) {
      document.cookie = 'preview=1; path=/';
    } else {
      document.cookie = 'preview=0; path=/';
    }
  });

  function getCookie(cname) {
      var name = cname + "=";
      var ca = document.cookie.split(';');
      for(var i=0; i<ca.length; i++) {
          var c = ca[i];
          while (c.charAt(0)==' ') c = c.substring(1);
          if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
      }
      return "";
  }

  if (getCookie('preview') == '1') {
    $editors.toggle();
    $previewToggle.prop('checked', true);
  }

});
