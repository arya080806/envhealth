export default {
  template: `
    <q-dialog @show="addClass" @hide="removeClass">
      <slot />
    </q-dialog>
  `,
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
