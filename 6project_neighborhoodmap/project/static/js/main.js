var nm = {map: null, page: null, curInfoWindow: null};

nm.part1 = '<div id="content">'+
           '<div id="siteNotice">'+
           '</div>'+
           '<h1 id="firstHeading" class="firstHeading">';

nm.part2 =  '</h1>'+
           '<div id="bodyContent">'+
           '<p><b>Uluru</b>, also referred to as <b>Ayers Rock</b>, is a large ' +
           'sandstone rock formation in the southern part of the '+
           'Northern Territory, central Australia. It lies 335&#160;km (208&#160;mi) '+
           'south west of the nearest large town, Alice Springs; 450&#160;km '+
           '(280&#160;mi) by road. Kata Tjuta and Uluru are the two major '+
           'features of the Uluru - Kata Tjuta National Park. Uluru is '+
           'sacred to the Pitjantjatjara and Yankunytjatjara, the '+
           'Aboriginal people of the area. It has many springs, waterholes, '+
           'rock caves and ancient paintings. Uluru is listed as a World '+
           'Heritage Site.</p>'+
           '<p>Attribution: Uluru, <a href="https://en.wikipedia.org/w/index.php?title=Uluru&oldid=297882194">'+
           'https://en.wikipedia.org/w/index.php?title=Uluru</a> '+
           '(last visited June 22, 2009).</p>'+
           '</div>'+
           '</div>';

nm.Location = function(latlng, info) {
  var self = this;

  this.latlng = latlng;
  this.info = info;

  this.marker = null;
  this.infoWindow = null;

  this.shouldShow = ko.observable(true);

  this.isVisible = ko.computed(function(){
    var isVisible = self.shouldShow();
    if(self.marker) {
      self.marker.setVisible(isVisible);
    }
    return isVisible;
  });
}

nm.Location.prototype.name = function() {
 return this.info.name;
}

nm.Location.prototype.onSelected = function() {
  var self = this;

  var curMarker = this.marker;
  curMarker.setAnimation(google.maps.Animation.BOUNCE);
  setTimeout(function(){ curMarker.setAnimation(null); }, 750);

  if (self.infoWindow != null) {
    this.showInfoWindow(self.infoWindow._content);
    return;
  }

  $.ajax({
     url: 'https://en.wikipedia.org/w/api.php?action=opensearch&limit=1&format=json&search=' + this.info.wikiTitle,
     dataType: 'jsonp',
   }).done(function(data) {
     var content = data[2][0];
     var bodyContent = content;

     var yelpUrl = '/get_location_info?title=' + self.info.yelpTitle;
     $.ajax({
       url: yelpUrl,
       dataType: 'json'
     }).done(function(data) {
       if (data['status'] != 'OK') {
         self.showInfoWindow(data['msg']);
         return;
       }
       window.console.log(data);

       bodyContent += '<br/><br/><div><b>Contact</b></div>';
       bodyContent += '<div>'+ data.biz.phone +'</div>';

       bodyContent += '<br/><div><b>Reviews</b></div>';
       bodyContent += '<div><img src="' + data.biz.rating_img_url + '"></img></div>';
       bodyContent += '<div>' + data.biz.snippet + '</div>';

       var htmlContent = '<div id="content">'+
             '<div id="siteNotice">'+
             '</div>'+
             '<h1 class="firstHeading">' + self.name() +
             '</h1>'+
             '<div id="bodyContent">' + bodyContent +
             '</div>'+
             '</div>';

       self.showInfoWindow(htmlContent);
     }).fail(function(data) {
       self.showInfoWindow('Getting location info failed !' + JSON.stringify(data));
     });

   }).fail(function(data) {
     self.showInfoWindow('Getting Wikipedia data failed! ');
  });

  self.showInfoWindow("Loading...");
}

nm.Location.prototype.setup = function() {
 this.marker = new google.maps.Marker({
     position: this.latlng,
     map: nm.map,
     animation: google.maps.Animation.DROP
 });

 this.marker.addListener('click', function() {
   this.onSelected();
 }.bind(this));
}

nm.Location.prototype.showInfoWindow = function(content) {
 this.infoWindow = new google.maps.InfoWindow({
     content: content
 });
 this.infoWindow._content = content;
 if (nm.curInfoWindow != null) {
   nm.curInfoWindow.close();
 }
 this.infoWindow.open(nm.page.map, this.marker);
 nm.curInfoWindow = this.infoWindow;
}


// Found on www.latlong.net
nm.locations = [
   new nm.Location(
     {lat: 37.785718, lng: -122.401051},
     {
       name: 'MOMA',
       wikiTitle: 'San_Francisco_Museum_of_Modern_Art',
       yelpTitle: 'Museum of Modern Art'
     }
   ),
   new nm.Location(
     {lat: 37.801436, lng: -122.458761},
     {
       name: 'Walt Disney Museum',
       wikiTitle: 'Walt_Disney_Family_Museum',
       yelpTitle: 'Walt Disney Family Museum'
     }
   ),
   new nm.Location(
     {lat: 37.771469, lng: -122.468676},
     {
       name: 'de Young Museum',
       wikiTitle: 'De_Young_(museum)',
       yelpTitle: 'de Young Museum'
     }
   ),
   new nm.Location(
     {lat: 37.786562, lng: -122.401361},
     {
       name: 'Museum of African Diaspora',
       wikiTitle: 'Museum_of_the_African_Diaspora',
       yelpTitle: 'Museum of The African Diaspora'
     }
   ),
   new nm.Location(
     {lat: 37.794704, lng: -122.411720},
     {
       name: 'Cable Car Museum',
       wikiTitle: 'San_Francisco_Cable_Car_Museum',
       yelpTitle: 'San Francisco Cable Car Museum'
     }
   ),
   new nm.Location(
     {lat: 37.806842, lng: -122.430675},
     {
       name: 'The Mexican Museum',
       wikiTitle: 'Mexican_Museum',
       yelpTitle: 'The Mexican Museum'
     }
   ),
   new nm.Location(
     {lat: 37.800843, lng: -122.398630},
     {
       name: 'The Exploratorium',
       wikiTitle: 'Exploratorium',
       yelpTitle: 'Exploratorium'
     }
   )
];

nm.filterLocations = function(searchPhrase, locations) {
  for (var i = 0; i < locations.length; i++) {
    var loc = locations[i];
    var shouldShow = loc.name().toLowerCase().indexOf(searchPhrase.toLowerCase()) != -1;
    loc.shouldShow(shouldShow);
  }
}

nm.LocationListViewModel = function() {
  var self = this

  self.museumSearchName = ko.observable("");

  self.searchByName = ko.computed(function() {
    var searchPhrase = self.museumSearchName();
    window.console.log(searchPhrase);
    nm.filterLocations(searchPhrase, nm.locations);
  });

  self.locations = ko.observableArray(nm.locations);

  self.locationClicked = function(loc) {
    loc.onSelected();
  }



  for(var i = 0; i < nm.locations.length; i++) {
    var loc = nm.locations[i];
    loc.setup();
  }
}

nm.Page = function() {
  this.openInfoWindow = null;
}

nm.Page.prototype.init = function() {



  nm.map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 37.760908, lng: -122.435004},
    zoom: 12
  });

  ko.applyBindings(new nm.LocationListViewModel());

  $("#menu-toggle").click(function(e) {
    e.preventDefault();
    $("#wrapper").toggleClass("toggled");
  });

  $('#mainrow').show();

};

nm.handleError = function() {
  alert("There was an error loading the application.");
}

nm.initMap = function() {
  nm.page = new nm.Page();
  nm.page.init();
}