import 'dart:async';
import 'package:core/core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart' as gmaps;

/// Service that handles device location queries and streams using Geolocator.
class LocationService {
  /// Check permissions and request them if needed.
  Future<bool> checkPermission() async {
    bool serviceEnabled;
    LocationPermission permission;

    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      return false;
    }

    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        return false;
      }
    }

    if (permission == LocationPermission.deniedForever) {
      return false;
    }

    return true;
  }

  /// Fetch current device location.
  Future<LatLng> getCurrentLocation() async {
    final hasPermission = await checkPermission();
    if (!hasPermission) {
      throw const PermissionDeniedException('Location permissions are denied');
    }

    final position = await Geolocator.getCurrentPosition();
    return LatLng(latitude: position.latitude, longitude: position.longitude);
  }

  /// Get active stream of device locations.
  Stream<LatLng> getLocationStream() {
    return Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 10,
      ),
    ).map(
      (position) => LatLng(
        latitude: position.latitude,
        longitude: position.longitude,
      ),
    );
  }
}

/// A reactive widget wrapping Google Map for tracking locations.
class TrackingMap extends StatefulWidget {
  const TrackingMap({
    required this.initialCenter,
    this.driverLocation,
    this.destinationLocation,
    this.sourceLocation,
    super.key,
  });

  final LatLng initialCenter;
  final LatLng? driverLocation;
  final LatLng? destinationLocation;
  final LatLng? sourceLocation;

  @override
  State<TrackingMap> createState() => _TrackingMapState();
}

class _TrackingMapState extends State<TrackingMap> {
  gmaps.GoogleMapController? _mapController;

  @override
  void didUpdateWidget(covariant TrackingMap oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.driverLocation != oldWidget.driverLocation &&
        widget.driverLocation != null) {
      _animateToPosition(widget.driverLocation!);
    }
  }

  void _animateToPosition(LatLng latLng) {
    if (_mapController != null) {
      unawaited(
        _mapController!.animateCamera(
          gmaps.CameraUpdate.newLatLng(
            gmaps.LatLng(latLng.latitude, latLng.longitude),
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final markers = <gmaps.Marker>{};

    if (widget.driverLocation != null) {
      markers.add(
        gmaps.Marker(
          markerId: const gmaps.MarkerId('driver'),
          position: gmaps.LatLng(
            widget.driverLocation!.latitude,
            widget.driverLocation!.longitude,
          ),
          icon: gmaps.BitmapDescriptor.defaultMarkerWithHue(
            gmaps.BitmapDescriptor.hueOrange,
          ),
          infoWindow: const gmaps.InfoWindow(title: 'Driver Location'),
        ),
      );
    }

    if (widget.destinationLocation != null) {
      markers.add(
        gmaps.Marker(
          markerId: const gmaps.MarkerId('destination'),
          position: gmaps.LatLng(
            widget.destinationLocation!.latitude,
            widget.destinationLocation!.longitude,
          ),
          icon: gmaps.BitmapDescriptor.defaultMarkerWithHue(
            gmaps.BitmapDescriptor.hueRed,
          ),
          infoWindow: const gmaps.InfoWindow(title: 'Destination'),
        ),
      );
    }

    if (widget.sourceLocation != null) {
      markers.add(
        gmaps.Marker(
          markerId: const gmaps.MarkerId('source'),
          position: gmaps.LatLng(
            widget.sourceLocation!.latitude,
            widget.sourceLocation!.longitude,
          ),
          icon: gmaps.BitmapDescriptor.defaultMarkerWithHue(
            gmaps.BitmapDescriptor.hueGreen,
          ),
          infoWindow: const gmaps.InfoWindow(title: 'Restaurant'),
        ),
      );
    }

    return gmaps.GoogleMap(
      initialCameraPosition: gmaps.CameraPosition(
        target: gmaps.LatLng(
          widget.initialCenter.latitude,
          widget.initialCenter.longitude,
        ),
        zoom: 15,
      ),
      onMapCreated: (controller) => _mapController = controller,
      markers: markers,
      myLocationEnabled: true,
    );
  }
}

/// Provider for LocationService.
final locationServiceProvider = Provider<LocationService>((ref) {
  return LocationService();
});
