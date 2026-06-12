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
export default {
  template: "<div></div>",
  mounted() {
    return __async(this, null, function* () {
      const { Plotly } = yield import("nicegui-plotly");
      this.Plotly = Plotly;
      this.update();
      this.$nextTick(() => {
        this.resizeObserver = new ResizeObserver(() => {
          var _a;
          if (((_a = this.options.config) == null ? void 0 : _a.responsive) === false) return;
          this.Plotly.Plots.resize(this.$el);
        });
        this.resizeObserver.observe(this.$el);
      });
    });
  },
  unmounted() {
    var _a;
    (_a = this.resizeObserver) == null ? void 0 : _a.disconnect();
  },
  methods: {
    update() {
      var _a;
      if (typeof this.Plotly === "undefined") {
        setTimeout(this.update, 10);
        return;
      }
      const options = this.options;
      if (((_a = options.config) == null ? void 0 : _a.responsive) === true) options.config.responsive = void 0;
      if (this.last_options && JSON.stringify(options.config) === JSON.stringify(this.last_options.config)) {
        this.Plotly.react(this.$el, this.options, options.config);
      } else {
        this.Plotly.newPlot(this.$el, this.options, options.config);
        this.set_handlers();
      }
      this.last_options = options;
    },
    set_handlers() {
      for (const name of [
        // source: https://plotly.com/javascript/plotlyjs-events/
        "plotly_click",
        "plotly_legendclick",
        "plotly_selecting",
        "plotly_selected",
        "plotly_hover",
        "plotly_unhover",
        "plotly_legenddoubleclick",
        "plotly_restyle",
        "plotly_relayout",
        "plotly_webglcontextlost",
        "plotly_afterplot",
        "plotly_autosize",
        "plotly_deselect",
        "plotly_doubleclick",
        "plotly_redraw",
        "plotly_animated"
      ]) {
        this.$el.on(name, (event) => {
          var _a;
          const args = __spreadProps(__spreadValues({}, event), {
            points: (_a = event == null ? void 0 : event.points) == null ? void 0 : _a.map((p) => __spreadProps(__spreadValues({}, p), {
              fullData: void 0,
              xaxis: void 0,
              yaxis: void 0
            })),
            xaxes: void 0,
            yaxes: void 0
          });
          this.$emit(name, args);
        });
      }
    }
  },
  data() {
    return {
      last_options: null
    };
  },
  props: {
    options: Object
  }
};
