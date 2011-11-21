/*
---
description:     LightFace.Request

authors:
  - David Walsh (http://davidwalsh.name)

license:
  - MIT-style license

requires:
  core/1.2.1:   '*'

provides:
  - LightFace.Request
...
*/
LightFace.Request = new Class({
	Extends: LightFace,
	options: {
		url: '',
		request: {
			url: false
		}
	},
	initialize: function(options) {
		this.parent(options);
		if(this.options.url) this.load();
	},
	/*
	load: function(url,title) {
		var props = (Object.append || $extend)({
			onRequest: function() {
				this.fade();
				this.fireEvent('request');
			}.bind(this),
			onSuccess: function(response) {
				this.messageBox.set('html',response);
				this.fireEvent('success');
			}.bind(this),
			onFailure: function() {
				this.messageBox.set('html',this.options.errorMessage);
				this.fireEvent('failure');
			}.bind(this),
			onComplete: function() {
				this._resize();
				this._ie6Size();
				this.messageBox.setStyle('opacity',1);
				this.unfade();
				this.fireEvent('complete');
			}.bind(this)
		},this.options.request);
		
		if(title && this.title) this.title.set('html',title);
		if(!props.url) props.url = url || this.options.url;
		
		new Request(props).send();
		return this;
	},
	*/
	loadex: function(url, method, data, container) {
		this.options.request.method = method;
		this.options.request.data = data;
		this.options.container = container;
		var props = (Object.append || $extend)({
			onRequest: function() {
				this.fade();
				this.fireEvent('request');
			}.bind(this),
			onSuccess: function(response) {
				console.log(this);
				console.log(this.options.container);
				this.options.container.set('html',response);
				/*
				else {
					this.messageBox.set('html',response);
				}
				*/
				this.fireEvent('success');
			}.bind(this),
			onFailure: function() {
				this.messageBox.set('html',this.options.errorMessage);
				this.fireEvent('failure');
			}.bind(this),
			onComplete: function() {
				this._resize();
				this._ie6Size();
				this.messageBox.setStyle('opacity',1);
				this.unfade();
				this.fireEvent('complete');
			}.bind(this)
		},this.options.request);
		
		if(!props.url) props.url = url || this.options.url;
		new Request(props).send();

		return this;
	}
});
