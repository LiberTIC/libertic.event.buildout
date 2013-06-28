
function initializeliberticevent(){

    $('#main-carousel').flexslider({
        slideshowSpeed: 4000,
      });
    $('#reusers-list').flexslider({
        animation: "slide",
        itemWidth: 140,
        itemMargin: 5,
        minItems: 2,
        maxItems: 6,
    });
    $('#suppliers-list').flexslider({
        animation: "slide",
        itemWidth: 140,
        itemMargin: 5,
        minItems: 2,
        maxItems: 6,
    });
    
     // Display event in a popup
    $('.link-event').prepOverlay({
        subtype: 'ajax',
        filter: common_content_filter,
        closeselector: '[name="form.button.Cancel"]',
        width:'40%'
    }); 
    
     // Display user in a popup
    $('.link-user').prepOverlay({
        subtype: 'ajax',
        filter: common_content_filter,
        closeselector: '[name="form.button.Cancel"]',
        width:'40%'
    }); 
}
jQuery(initializeliberticevent);
