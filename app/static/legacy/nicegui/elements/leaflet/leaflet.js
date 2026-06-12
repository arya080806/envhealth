var __defProp = Object.defineProperty;
var __defProps = Object.defineProperties;
var __getOwnPropDescs = Object.getOwnPropertyDescriptors;
var __getOwnPropSymbols = Object.getOwnPropertySymbols;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __propIsEnum = Object.prototype.propertyIsEnumerable;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __spreadValues = (a, b) => {
  for (var prop in b || (b = {}))
    if (__hasOwnProp.call(b, prop))
      __defNormalProp(a, prop, b[prop]);
  if (__getOwnPropSymbols)
    for (var prop of __getOwnPropSymbols(b)) {
      if (__propIsEnum.call(b, prop))
        __defNormalProp(a, prop, b[prop]);
    }
  return a;
};
var __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));
var __objRest = (source, exclude) => {
  var target = {};
  for (var prop in source)
    if (__hasOwnProp.call(source, prop) && exclude.indexOf(prop) < 0)
      target[prop] = source[prop];
  if (source != null && __getOwnPropSymbols)
    for (var prop of __getOwnPropSymbols(source)) {
      if (exclude.indexOf(prop) < 0 && __propIsEnum.call(source, prop))
        target[prop] = source[prop];
    }
  return target;
};
var __async = (__this, __arguments, generator) => {
  return new Promise((resolve, reject) => {
    var fulfilled = (value) => {
      try {
        step(generator.next(value));
      } catch (e) {
        reject(e);
      }
    };
    var rejected = (value) => {
      try {
        step(generator.throw(value));
      } catch (e) {
        reject(e);
      }
    };
    var step = (x) => x.done ? resolve(x.value) : Promise.resolve(x.value).then(fulfilled, rejected);
    step((generator = generator.apply(__this, __arguments)).next());
  });
};
import { leaflet as L } from "nicegui-leaflet";
import { loadResource } from "../../static/utils/resources.js";
import { cleanObject } from "../../static/utils/json.js";
export default {
  template: "<div></div>",
  props: {
    center: Array,
    zoom: Number,
    options: Object,
    drawControl: Object,
    resourcePath: String,
    hideDrawnItems: Boolean,
    additionalResources: Array
  },
  mounted() {
    return __async(this, null, function* () {
      yield this.$nextTick();
      yield loadResource(window.path_prefix + `${this.resourcePath}/leaflet/leaflet.css`);
      window.L = L;
      yield Promise.all(this.additionalResources.map((resource) => loadResource(resource)));
      if (this.drawControl) {
        yield Promise.all([
          loadResource(window.path_prefix + `${this.resourcePath}/leaflet-draw/leaflet.draw.css`),
          loadResource(window.path_prefix + `${this.resourcePath}/leaflet-draw/leaflet.draw.js`)
        ]);
      }
      this.map = L.map(this.$el, __spreadProps(__spreadValues({}, this.options), {
        center: this.center,
        zoom: this.zoom
      }));
      for (const type of [
        "baselayerchange",
        "overlayadd",
        "overlayremove",
        "zoomlevelschange",
        "resize",
        "unload",
        "viewreset",
        "load",
        "zoomstart",
        "movestart",
        "zoom",
        "move",
        "zoomend",
        "moveend",
        "popupopen",
        "popupclose",
        "autopanstart",
        "tooltipopen",
        "tooltipclose",
        "locationerror",
        "locationfound",
        "click",
        "dblclick",
        "mousedown",
        "mouseup",
        "mouseover",
        "mouseout",
        "mousemove",
        "contextmenu",
        "keypress",
        "keydown",
        "keyup",
        "preclick",
        "zoomanim"
      ]) {
        this.map.on(type, (e) => {
          this.$emit(`map-${type}`, __spreadProps(__spreadValues({}, e), {
            originalEvent: void 0,
            target: void 0,
            sourceTarget: void 0,
            center: [e.target.getCenter().lat, e.target.getCenter().lng],
            zoom: e.target.getZoom()
          }));
        });
      }
      for (const type of ["layeradd", "layerremove"]) {
        this.map.on(type, (e) => {
          this.$emit(`map-${type}`, {
            id: e.layer.id,
            leaflet_id: e.layer._leaflet_id
          });
        });
      }
      if (this.drawControl) {
        for (const key in L.Draw.Event) {
          const type = L.Draw.Event[key];
          this.map.on(type, (e) => __async(this, null, function* () {
            yield this.$nextTick();
            const cleanedObject = cleanObject(e, [
              "_map",
              "_events",
              "_eventParents",
              "_handlers",
              "_mapToAdd",
              "_initHooksCalled"
            ]);
            this.$emit(type, __spreadProps(__spreadValues({}, cleanedObject), {
              target: void 0,
              sourceTarget: void 0
            }));
          }));
        }
        const originalType = window.type;
        window.type = "Feature";
        const drawnItems = new L.FeatureGroup();
        window.type = originalType;
        this.map.addLayer(drawnItems);
        const dc = this.drawControl && typeof this.drawControl === "object" ? this.drawControl : {};
        const drawOptions = dc.draw === true || dc.draw === void 0 ? {} : dc.draw || {};
        let editOptions = dc.edit === true || dc.edit === void 0 ? {} : dc.edit || {};
        if (typeof editOptions === "object" && "edit" in editOptions) {
          const _a = editOptions, { edit: _ignoredEditFlag } = _a, rest = __objRest(_a, ["edit"]);
          editOptions = rest;
        }
        const drawControl = new L.Control.Draw({
          draw: drawOptions,
          edit: __spreadProps(__spreadValues({}, editOptions), {
            featureGroup: drawnItems
          })
        });
        this.map.addControl(drawControl);
        if (!this.hideDrawnItems) {
          this.map.on("draw:created", (e) => drawnItems.addLayer(e.layer));
        }
      }
      const connectInterval = setInterval(() => __async(this, null, function* () {
        if (window.socket.id === void 0) return;
        this.$emit("init");
        clearInterval(connectInterval);
      }), 100);
      this.observer = new IntersectionObserver(([entry]) => {
        if (entry.isIntersecting) this.run_map_method("invalidateSize");
      });
      this.observer.observe(this.$el);
    });
  },
  unmounted() {
    var _a;
    (_a = this.observer) == null ? void 0 : _a.disconnect();
  },
  methods: {
    add_layer(layer, id) {
      let obj = L;
      for (const part of layer.type.split(".")) {
        obj = obj[part];
      }
      const l = obj(...layer.args);
      l.id = id;
      l.addTo(this.map);
    },
    remove_layer(id) {
      this.map.eachLayer((layer) => layer.id === id && this.map.removeLayer(layer));
    },
    clear_layers() {
      this.map.eachLayer((layer) => this.map.removeLayer(layer));
    },
    run_map_method(name, ...args) {
      if (name.startsWith(":")) {
        name = name.slice(1);
        args = args.map((arg) => new Function(`return (${arg})`)());
      }
      return runMethod(this.map, name, args);
    },
    run_layer_method(id, name, ...args) {
      let result = null;
      this.map.eachLayer((layer) => {
        if (layer.id !== id) return;
        if (name.startsWith(":")) {
          name = name.slice(1);
          args = args.map((arg) => new Function(`return (${arg})`)());
        }
        result = runMethod(layer, name, args);
      });
      return result;
    }
  }
};
