export default {
  template: "<div></div>",
  async mounted() {
    const { Plotly } = await import("nicegui-plotly");
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
          const args = {
            ...event,
            points: (_a = event == null ? void 0 : event.points) == null ? void 0 : _a.map((p) => ({
              ...p,
              fullData: void 0,
              xaxis: void 0,
              yaxis: void 0
            })),
            xaxes: void 0,
            yaxes: void 0
          };
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
