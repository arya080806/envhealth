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
import { echarts, loadEchartsGL } from "nicegui-echart";
import { convertDynamicProperties } from "../../static/utils/dynamic_properties.js";
export default {
  template: "<div></div>",
  mounted() {
    return __async(this, null, function* () {
      yield new Promise((resolve) => setTimeout(resolve, 0));
      if (this.enable3d) {
        yield loadEchartsGL();
      }
      const theme_name = this.theme ? createRandomUUID() : null;
      try {
        if (typeof this.theme == "string") {
          const response = yield fetch(this.theme);
          echarts.registerTheme(theme_name, yield response.json());
        } else if (this.theme) {
          echarts.registerTheme(theme_name, this.theme);
        }
      } catch (error) {
        console.error("Could not register theme:", error);
      }
      this.chart = echarts.init(this.$el, theme_name, { renderer: this.renderer });
      this.chart.on("click", (e) => this.$emit("componentClick", e));
      for (const event of [
        "click",
        "dblclick",
        "mousedown",
        "mousemove",
        "mouseup",
        "mouseover",
        "mouseout",
        "globalout",
        "contextmenu",
        "highlight",
        "downplay",
        "selectchanged",
        "legendselectchanged",
        "legendselected",
        "legendunselected",
        "legendselectall",
        "legendinverseselect",
        "legendscroll",
        "datazoom",
        "datarangeselected",
        "graphroam",
        "georoam",
        "treeroam",
        "timelinechanged",
        "timelineplaychanged",
        "restore",
        "dataviewchanged",
        "magictypechanged",
        "geoselectchanged",
        "geoselected",
        "geounselected",
        "axisareaselected",
        "brush",
        "brushEnd",
        "brushselected",
        "globalcursortaken",
        "rendered",
        "finished"
      ]) {
        this.chart.on(event, (e) => this.$emit(`chart:${event}`, e));
      }
      let initialResizeTriggered = false;
      const initialWidth = this.$el.offsetWidth;
      const initialHeight = this.$el.offsetHeight;
      this.resizeObserver = new ResizeObserver(() => {
        if (!initialResizeTriggered) {
          initialResizeTriggered = true;
          if (this.$el.offsetWidth === initialWidth && this.$el.offsetHeight === initialHeight) {
            return;
          }
        }
        this.chart.resize();
      }).observe(this.$el);
      this.update_chart();
    });
  },
  beforeUnmount() {
    this.chart.dispose();
  },
  unmounted() {
    var _a;
    (_a = this.resizeObserver) == null ? void 0 : _a.disconnect();
  },
  methods: {
    update_chart() {
      var _a, _b, _c;
      if (!this.chart) {
        setTimeout(this.update_chart, 10);
        return;
      }
      convertDynamicProperties(this.options, true);
      this.chart.setOption(this.options, {
        notMerge: ((_b = (_a = this.chart.getOption()) == null ? void 0 : _a.series) == null ? void 0 : _b.length) != ((_c = this.options.series) == null ? void 0 : _c.length)
      });
    },
    run_chart_method(name, ...args) {
      if (name.startsWith(":")) {
        name = name.slice(1);
        args = args.map((arg) => new Function(`return (${arg})`)());
      }
      return runMethod(this.chart, name, args);
    }
  },
  props: {
    options: Object,
    enable3d: Boolean,
    renderer: String,
    theme: String
  }
};
