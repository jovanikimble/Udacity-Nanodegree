var nm = {map: null, page: null};

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

 if (nm.page.openInfoWindow) {
   nm.page.openInfoWindow.close();
 }
 this.infoWindow.open(nm.page.map, curMarker);
 nm.page.openInfoWindow = this.infoWindow;
}

nm.Location.prototype.setup = function() {
 this.marker = new google.maps.Marker({
     position: this.latlng,
     map: nm.map,
     animation: google.maps.Animation.DROP
 });

 this.infoWindow = new google.maps.InfoWindow({
       content: nm.part1 + this.name() + nm.part2
 });

 this.marker.addListener('click', function() {
   this.onSelected();
 }.bind(this));
}


// Found on www.latlong.net
nm.locations = [
   new nm.Location(
     {lat: 37.785718, lng: -122.401051},
     {name: 'MOMA'}
   ),
   new nm.Location(
     {lat: 37.801436, lng: -122.458761},
     {name: 'Walt Disney Museum'}
   ),
   new nm.Location(
     {lat: 37.771469, lng: -122.468676},
     {name: 'de Young Museum'}
   ),
   new nm.Location(
     {lat: 37.786562, lng: -122.401361},
     {name: 'Museum of African Diaspora'}
   ),
   new nm.Location(
     {lat: 37.794704, lng: -122.411720},
     {name: 'Cable Car Museum'}
   ),
   new nm.Location(
     {lat: 37.806842, lng: -122.430675},
     {name: 'The Mexican Museum'}
   ),
   new nm.Location(
     {lat: 37.800843, lng: -122.398630},
     {name: 'The Exploratorium'}
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

nm.initMap = function() {
  nm.page = new nm.Page();
  nm.page.init();
}