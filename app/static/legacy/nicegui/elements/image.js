export default {
  template: '\n    <component :is="tag || \'q-img\'" ref="qRef" :src="computed_src">\n      <template v-for="(_, slot) in $slots" v-slot:[slot]="slotProps">\n        <slot :name="slot" v-bind="slotProps || {}" />\n      </template>\n    </component>\n  ',
  props: {
    src: String,
    t: String,
    tag: String
  },
  data: function() {
    return {
      computed_src: void 0
    };
  },
  mounted() {
    setTimeout(() => this.compute_src(), 0);
  },
  updated() {
    this.compute_src();
  },
  methods: {
    compute_src() {
      const suffix = this.t ? (this.src.includes("?") ? "&" : "?") + "_nicegui_t=" + this.t : "";
      this.computed_src = (this.src.startsWith("/") ? window.path_prefix : "") + this.src + suffix;
    }
  }
};
