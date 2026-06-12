export default {
  template: `<q-header ref="qRef"><slot></slot></q-header>`,
  mounted() {
    if (this.addScrollPadding) {
      this.resizeObserver = new ResizeObserver(() => {
        document.documentElement.style.scrollPaddingTop = `${this.$el.offsetHeight}px`;
      }).observe(this.$el);
    }
  },
  unmounted() {
    var _a;
    (_a = this.resizeObserver) == null ? void 0 : _a.disconnect();
  },
  props: {
    addScrollPadding: Boolean
  }
};
