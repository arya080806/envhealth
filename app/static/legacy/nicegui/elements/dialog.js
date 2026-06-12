export default {
  template: '\n    <q-dialog @show="addClass" @hide="removeClass">\n      <slot />\n    </q-dialog>\n  ',
  methods: {
    addClass() {
      document.documentElement.classList.add("nicegui-dialog-open");
    },
    removeClass() {
      document.documentElement.classList.remove("nicegui-dialog-open");
    }
  },
  unmounted() {
    this.removeClass();
  }
};
