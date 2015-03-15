{
	|test|
	var viewTypes, propertyTests, doPropertyTest;

	viewTypes = [
		View, Button, CheckBox, CompositeView, DragBoth, DragSink, DragSource,
		EnvelopeView, LevelIndicator, MultiSliderView, FreqScopeView,
		Knob, ListView, NumberBox, PopUpMenu, ScopeView, UserView, WebView,
		RangeSlider, Slider, Slider2D, SoundFileView, StaticText, TextView, TreeView
	];

	propertyTests = (
		\bounds: Rect(123, 321, 210, 321),
		\visible: false,
		\enabled: false,
		\background: Color.blue
	);

	doPropertyTest = {
		| test, view |
		var viewName = view.class.name.asString;

		propertyTests.keysValuesDo {
			|prop, val|
			var propSetter = (prop ++ "_").asSymbol, current = view.perform(prop);
			view.perform(propSetter, val);
			0.001.wait;
			test.assertEquals(view.perform(prop), val, viewName ++ "." ++ prop ++ " is settable and gettable.");
			view.perform(propSetter, current);
		}
	};


	viewTypes.do {
		|viewClass|
		var view = viewClass.new(), viewName = view.class.name.asString;
		test.assert(view.bounds.width >= 0, viewName ++ " has coordinates.");
		test.assert(view.visible.not, viewName ++ " is not visible when created.");

		view.front; 0.001.wait;
		test.assert(view.visible(), viewName ++ " is visible after .front().");

		doPropertyTest.value(test, view);

		view.close(); 0.001.wait;
		test.assert(view.isValid.not, viewName ++ " is invalidated after .close().");
	}
}