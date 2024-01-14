let autocomplete;

function initAutoComplete() {
  var elAddress = document.getElementById( 'id_address' )
  if( elAddress ) {
    autocomplete = new google.maps.places.Autocomplete(
      elAddress, {
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code
        componentRestrictions: {'country': ['us']},
    })
    // function to specify what should happen when the prediction is clicked
    autocomplete.addListener( 'place_changed', onPlaceChanged );
  }
}

function onPlaceChanged () {
  var place = autocomplete.getPlace();

  // User did not select the prediction. Reset the input field or alert()
  if( !place.geometry ) {
    document.getElementById( 'id_address' ).placeholder = "Start typing...";
  } else {
    console.log('place name=>', place.name)
  }
  // get the address components and assign them to the fields

  // get the address components and assign them to the fields
  // console.log(place);
  var geocoder = new google.maps.Geocoder()
  var address = document.getElementById('id_address').value

  geocoder.geocode({ 'address': address}, function( results, status ) {
    // console.log('status=>', status)
    if( status == google.maps.GeocoderStatus.OK ) {
      var latitude = results[ 0 ].geometry.location.lat();
      var longitude = results[ 0 ].geometry.location.lng();

      // console.log('lat=>', latitude);
      // console.log('long=>', longitude);
      $( '#id_latitude' ).val( latitude );
      $( '#id_longitude' ).val( longitude );

      $( '#id_address' ).val( address );
    }
  });

  // loop through the address components and assign other address data
  // console.log(place.address_components);
  for( var i = 0; i < place.address_components.length; i++ ) {
    for( var j = 0; j < place.address_components[ i ].types.length; j++){
      // get country
      var fn = place.address_components[ i ].types[ j ]
      if( fn == 'country') {
        $( '#id_country' ).val(place.address_components[i].long_name);
      }
      // get state
      if( fn == 'administrative_area_level_1') {
        $( '#id_state' ).val(place.address_components[i].long_name);
      }
      // get city
      if( fn == 'locality') {
        $( '#id_city' ).val(place.address_components[i].long_name);
      }
      // get pincode
      if( fn == 'postal_code') {
        $( '#id_pin_code' ).val(place.address_components[i].long_name);
     }
    }
  }

}

$( document ).ready( function () {
  $( '.add-to-cart' ).on( 'click', function( e ) {
    e.preventDefault();
    food_id = $( this ).attr( 'data-id' )
    url = $( this ).attr( 'data-url' )
    $.ajax({
      type: 'GET',
      url: url,
      success: function( response ) {
        if( response.status == 'login' ) {
          swal( response.message, '', 'info').then( function() {
            window.location = '/login'
          })
        } else if( response.status == 'success' ) {
          console.log( `tax_list=${response.cart_totals.tax_list}`)
          $( '#cart_counter' ).html( response.cart_counter[ 'cart_count' ])
          $( '#qty-' + food_id ).html( response.qty )
          display_cart_totals( response.cart_totals )
        } else {
          swal( response.message, '', 'error')
        }
      }
    })
  })

  $( '.decrease-cart' ).on( 'click', function( e ) {
    e.preventDefault();
    food_id = $( this ).attr( 'data-id' )
    cart_id = $( this ).attr( 'data-cart-id' )
    url = $( this ).attr( 'data-url' )
    $.ajax({
      type: 'GET',
      url: url,
      success: function( response ) {
        if( response.status == 'login' ) {
          swal( response.message, '', 'info').then( function() {
            window.location = '/login'
          })
        } else if( response.status == 'success' ) {
          $( '#cart_counter' ).html( response.cart_counter[ 'cart_count' ])
          display_cart_totals( response.cart_totals )
          if( response.qty <= 0 ) {
            $( '#cart-' + cart_id ).remove()
            check_empty_cart()
          } else {
            $( '#qty-' + food_id ).html( response.qty )
          }
        } else {
          swal( response.message, '', 'error')
        }
      },
    })
  })

  $( '.delete-cart' ).on( 'click', function( e ) {
    e.preventDefault();
    cart_id = $( this ).attr( 'data-id' )
    url = $( this ).attr( 'data-url' )
    $.ajax({
      type: 'GET',
      url: url,
      success: function( response ) {
        if( response.status == 'login' ) {
          swal( response.message, '', 'info').then( function() {
            window.location = '/login'
          })
        } else if( response.status == 'success' ) {
          $( '#cart_counter' ).html( response.cart_counter[ 'cart_count' ])
          $( '#cart-' + cart_id ).remove()
          display_cart_totals( response.cart_totals )
          check_empty_cart()
          swal( response.message, '', 'success')
        } else {
          swal( response.message, '', 'error')
        }
      },
    })
  })

  $('.item_qty').each( function() {
    var line_id = $( this ).attr( 'id' )
    var qty = $( this ).attr( 'data-qty' )
    $( '#' + line_id ).html( qty )
  })
  check_empty_cart()

  function check_empty_cart() {
    var cart_count = $( '#cart_counter' ).text()
    var el_empty_cart = $( '#empty_cart' )
    if( cart_count == 0 ) {
      el_empty_cart.show()
    } else {
      el_empty_cart.hide()
    }
  }

  function display_cart_totals( cart_totals ) {
    $( '#subtotal' ).html( cart_totals[ 'subtotal' ])
    cart_totals[ 'tax_list' ].forEach( ( tax, i) => {
      console.log( `#tax-${i} = ${tax[ 'amount' ]}`)
      $( '#tax-' + i ).html( tax[ 'amount' ] )
    })
    $( '#tax' ).html( cart_totals[ 'tax_list' ])
    $( '#total' ).html( cart_totals[ 'grand_total' ])
  }

  $( '.add-hour' ).on( 'click', function( e ) {
    e.preventDefault();
    console.log( 'add-hour' );
    var day = document.getElementById( 'id_day' ).value
    var from_hour = document.getElementById( 'id_from_hour' ).value
    var to_hour = document.getElementById( 'id_to_hour' ).value
    var is_closed = document.getElementById( 'id_is_closed' ).checked
    var url = document.getElementById( 'add_hour_url' ).value
    var csrf_token = $( 'input[name=csrfmiddlewaretoken]' ).val()
    if( day != '' 
          && ( from_hour != '' && to_hour != '' ) || is_closed ) {
      $.ajax({
        type: 'POST',
        url: url,
        data: {
          'day': day,
          'from_hour': from_hour,
          'to_hour': to_hour,
          'is_closed': is_closed,
          'csrfmiddlewaretoken': csrf_token,
        },
        success: function( response ) {
          if( response.status == 'success' ) {
            if(response.is_closed == 'Closed') {
              html = `<td>Closed</td>`
            } else {
              html = `<td>${response.from_hour} - ${response.to_hour}</td>`
            }
            html = `<tr id="hour-${response.id}">`
              + `<td><b>${response.day}</b></td>`
              + html
              + `<td><a href="#" class="remove_hour" data-url="/vendor/opening-hours/remove/${response.id}/">Remove</a></td>`
              + '</tr>'

            $(".opening_hours").append(html)
            document.getElementById("opening_hours").reset();
          } else {
            swal( response.message, '', "error" )
          }
        },
      })
    } else {
      swal( 'Please complete all fields', '', 'info' )
    }
  })

  $( document ).on( 'click', '.remove-hour', function( e ) {
    e.preventDefault();
    url = $( this ).attr( 'data-url' );
    console.log( url );
    $.ajax({
      type: 'GET',
      url: url,
      success: function( response ) {
        if( response.status == 'success' ) {
          console.log( $( '#hour-' + response.id ).html() )
          $( '#hour-' + response.id ).remove();
        }
      }
    });
  });
});