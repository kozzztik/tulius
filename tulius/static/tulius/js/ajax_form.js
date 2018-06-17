// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function() {
    $('.ajaxform .btn-primary').unbind();
    $('.ajaxform .btn-primary').click(function() {
        var ajax_indicator = $(this).after('<i class="icon-spinner icon-spin icon-2x"></i>');
        $(this).hide();
        var modal = $(this).parents('.ajaxform');
        var form = $(modal).find('form');
        var action = form.attr('action');
        $(modal).find('input, select, textbox').attr('readonly', 'true');
        $(modal).find('.alert').remove();
        form.ajaxSubmit({
            url: action,
            dataType: 'json',
            success: function(data, statusText, xhr, $form) {
                if (data['result']) {
                    window.location.replace(data['redirect']);
                } else { 
                    $(form).replaceWith(data['html']);
                    $(this).show();
                    $(modal).find('.alert').remove();
                    $(modal).find('i.icon-spinner').remove();
                    $(modal).find('.btn-primary').show();
                }
            },
            error: function( jqXHR, textStatus, errorThrown ) {
                $(modal).find('i.icon-spinner').remove();
                $(modal).find('.btn-primary').show();
                var form = $(modal).find('form').before('<div class="alert alert-error">' + errorThrown + '</div>');
                $(modal).find('input, select, textbox').removeAttr('readonly');
            }
        });
        
    });
    
});

function add_formset_item(selector) {
        var formset = $('#' + selector);
        var add_button = $(formset).find('.add-link');
        var ajax_indicator = $(add_button).after('<i class="icon-spinner icon-spin"></i>');
        $(add_button).hide();
        var form = $(formset).find('.ajax-add-form');
        var action = formset.attr('formset_url');
        $(form).find('input, select, textbox').attr('readonly', 'true');
        $(formset).find('.ajax-errors').remove();
        form.ajaxSubmit({
            url: action,
            type: 'POST',
            dataType: 'html',
            success: function(data, statusText, xhr, $form) {
                $(formset).replaceWith(data);
            },
            error: function( jqXHR, textStatus, errorThrown ) {
                $(formset).find('i.icon-spinner').remove();
                $(formset).find('.add-link').show();
                $(form).before('<div class="alert alert-error ajax-errors">' + errorThrown + '</div>');
                $(formset).find('input, select, textbox').removeAttr('readonly');
            }
        });
        
};

function delete_formset_item(selector) {
        var row = $('#' + selector);
        var item_id = $(row).attr('item_id');
        var formset = $(row).parents('.ajax-formset');
        var delete_button = $(row).find('.delete-link');
        var ajax_indicator = $(delete_button).after('<i class="icon-spinner icon-spin"></i>');
        $(delete_button).hide();
        var action = formset.attr('formset_url');
        $(formset).find('.ajax-errors').remove();
        $.ajax({
            url: action,
            type: 'POST',
            dataType: 'html',
            data: {item_id: item_id},
            success: function(data, statusText, xhr, $form) {
                $(formset).replaceWith(data);
            },
            error: function( jqXHR, textStatus, errorThrown ) {
                $(formset).find('i.icon-spinner').remove();
                $(formset).find('.delete-link').show();
                $(row).before('<div class="alert alert-error ajax-errors">' + errorThrown + '</div>');
            }
        });
        
};