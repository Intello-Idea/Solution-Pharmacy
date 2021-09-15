window.onscroll = function () {
    scrollFunction();
    navFunction();
};
window.onresize = function () {
    navWidth();
};
window.onload = function () {
    init();
};

function init() {
    //alert(parseInt(document.getElementById('valueFilter').innerHTML))

    var w = window.innerWidth;
    if (!(w < 992)) {

        if (document.body.scrollTop > 70 || document.documentElement.scrollTop > 70) {
            document.getElementById('sticky-header').classList.add("sticky");

        } else {
            document.getElementById('sticky-header').classList.remove("sticky", "mt-1", "nav_ep");
        }
    } else {
        if (!(document.getElementById('oe_main_menu_navbar'))) {
            document.getElementById('sticky-header').classList.remove("nav_ep", "mt-1");
        } else {
            document.getElementById('sticky-header').classList.add("mt-1", "nav_ep");
        }

    }
    var filterValue = parseInt(document.getElementById('valueFilter').innerHTML);
    document.getElementById('selectFilter').value = filterValue;
    // initialisation stuff here

}

function valueSelectFilterMap() {
    var select = document.getElementById('selectFilter').value
    //alert(window.location+"home/id_filter_map="+select)
    href = location.origin + "/home/" + "id_filter_map=" + select + "#section-map"
    window.location.replace(href);


    //var t = document.getElementById("valueFilter2");
    //t.innerHTML = select
    //t.setAttribute("t-set","foo")
    //t.setAttribute("t-value","2")
    //  alert(t.innerHTML)

}

function scrollFunction() {
    if (document.body.scrollTop > 70 || document.documentElement.scrollTop > 70) {
        document.getElementById('sticky-header').classList.add("sticky", "mt-1", "nav_ep");
        if (!(document.getElementById('oe_main_menu_navbar'))) {
            document.getElementById('sticky-header').classList.remove("nav_ep", "mt-1");
        }
    } else {
        var w = window.innerWidth;
        if (!(w < 992)) {
            document.getElementById('sticky-header').classList.remove("sticky", "nav_ep", "mt-1");
        }
    }
};

function navFunction() {
    if (document.body.scrollTop > 70 || document.documentElement.scrollTop > 70) {
        document.getElementById('fa-color').classList.remove("fa-green")
        document.getElementById('fa-color').classList.add("fa-white")
    } else {
        var w = window.innerWidth;
        if (w < 992) {
            document.getElementById('fa-color').classList.remove("fa-green")
            document.getElementById('fa-color').classList.add("fa-white")
        } else {
            document.getElementById('fa-color').classList.remove("fa-white")
            document.getElementById('fa-color').classList.add("fa-green")
        }
    }

};

function navWidth() {
    var w = window.innerWidth;
    if (w < 992) {
        if ((document.getElementById('oe_main_menu_navbar'))) {
            document.getElementById('sticky-header').classList.add("mt-1", "nav_ep");

        } else {
            document.getElementById('sticky-header').classList.remove("nav_ep", "mt-1");
        }
        document.getElementById('sticky-header').classList.add("sticky");
        document.getElementById('fa-color').classList.remove("fa-green")
        document.getElementById('fa-color').classList.add("fa-white")
    } else {
        document.getElementById('sticky-header').classList.remove("sticky", "mt-1", "nav_ep")
        document.getElementById('fa-color').classList.remove("fa-white")
        document.getElementById('fa-color').classList.add("fa-green")
    }
};


// Initialize and add the map
function initMap() {
    var loc = document.getElementById('list-group').getElementsByTagName('a')[0];


    var location = {lat: parseFloat(loc.getAttribute("lat")), lng: parseFloat(loc.getAttribute("lng"))};
    // The map, centered at Uluru
    var map = new google.maps.Map(
        document.getElementById('map'), {zoom: 14, center: location, streetViewControl: false});
    // The marker, positioned at Uluru
    var marker = new google.maps.Marker({position: location, map: map});
}

function locationMap(lat, lng) {
    if ((lat == 0) && (lng == 0)) {
        alert("No se encontro la ubicacion en google maps")
    } else {
        // The location of Uluru
        var location = {lat: lat, lng: lng};
        // The map, centered at Uluru
        var map = new google.maps.Map(
            document.getElementById('map'), {zoom: 18, center: location, streetViewControl: false});
        // The marker, positioned at Uluru
        var marker = new google.maps.Marker({position: location, map: map});

    }

};

// Inicio - JS for Product Carrousel in Category Page
//var $ = document;

/*
$.addEventListener('DOMContentLoaded', function() {

  const sliderMe = () => {
    let currentPosition = 0,
      sliderItem = document.querySelectorAll('.slider-item'),
      sliderItemWidth = window
      .getComputedStyle(sliderItem[0])
      .flexBasis.match(/\d+\.?\d+/g),
      sliderInner = $.querySelector('.slider-inner'),

      control = {
        next: $.querySelector('#next'),
        slideNext() {
          currentPosition += parseFloat(sliderItemWidth);
          if (currentPosition > limitPosition) {
            currentPosition = 0;
          }
          sliderInner.style.right = currentPosition + '%';
        },
        prev: $.querySelector('#prev'),
        slidePrev() {
          currentPosition -= parseFloat(sliderItemWidth);
          if (currentPosition < 0) {
            currentPosition = limitPosition;
          }
          sliderInner.style.right = currentPosition + '%';
        }
      },
      limitPosition = sliderItemWidth * (sliderItem.length - Math.floor(100 / sliderItemWidth));

    control.next.addEventListener('click', control.slideNext)
    control.prev.addEventListener('click', control.slidePrev)

    window.addEventListener("resize",function(){
      currentPosition = 0;
      $.querySelector('.slider-inner').style.right = currentPosition + '%';
    })
  }
  sliderMe();

  window.addEventListener("resize", sliderMe)

});
*/
// Fin - JS for Product Carrousel in Category Page