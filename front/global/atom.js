HALF_DIM = view.viewSize.width / 2;
CIRCLE_RADIUS = HALF_DIM / 20;
ELECTRON_SPEED = 1;

function ellipse(rotate) {
   RADIUS = 0.85 * HALF_DIM;
   var res = new Path.Ellipse({
      center: [HALF_DIM, HALF_DIM],
      radius: [RADIUS, RADIUS * 0.25],
      strokeColor: '#F7F7F7',
      strokeWidth: 1
   });
   res.rotate(rotate || 0)
   return res;
}

function circle(center) {
   console.log(center);
   return new Shape.Circle({
      center: center,
      radius: CIRCLE_RADIUS,
      strokeColor: '#F7F7F7',
      strokeWidth: 1,
      fillColor: '#F7F7F7'
   });
}

function moveToTime(bundles, time) {
   bundles.forEach(function(bundle) {
      bundle['electron'].position = bundle['ellipse'].getPointAt(
            (bundle['timeOffset'] + time * ELECTRON_SPEED) % 4, true);
   });
}

var ellipses = [
   {'ellipse': ellipse(90), 'timeOffset': 0.3},
   {'ellipse': ellipse(30), 'timeOffset': 2.3},
   {'ellipse': ellipse(-30), 'timeOffset': 0.3}
];

ellipses.forEach(function(bundle) { 
   bundle['electron'] = circle(bundle['ellipse'].getPointAt(bundle['timeOffset'], true));
});

function onFrame(event) {
   if (window.ELECTRON_PLAY)
      moveToTime(ellipses, event.time);
}