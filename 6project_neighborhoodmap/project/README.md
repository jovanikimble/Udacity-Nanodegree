# Neigborhood Map

This is a single page application featuring a map of San Franciso and a few of
its museums.

## Motivation

Motivation behind this application was to get more comforatble using different
API's together. This application features Google Maps JavaScript API and the
Yelp API abd an understanding of Knockout.js.

## Code Example

Location Marker and Info window functionality snippet
```
nm.Location.prototype.onSelected = function() {
  var self = this;

  var curMarker = this.marker;
  curMarker.setAnimation(google.maps.Animation.BOUNCE);
  setTimeout(function(){ curMarker.setAnimation(null); }, 750);

  if (self.infoWindow != null) {
    this.showInfoWindow(self.infoWindow._content);
    return;
  }
```
Using third party code

`import httplib2`
`import json`
`import flask`
`import random, string`

## Installation

Make sure you have **python downloaded and installed.**

If not, download [here](https://www.python.org/downloads/)

Next, clone the following repository:

[HERE](https://github.com/jovanikimble/Udacity-Nanodegree.git)

`cd` to this directory:

$ Udacity-Nanodegree/6project_neighborhood map/project/

To run the Neighborhood Map, do the following in the terminal:

$ pip install requirements.txt
$ python main.py

One time Set up only:

Navigate to http://localhost:10000