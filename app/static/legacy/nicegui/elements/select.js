export default {
  props: ["options"],
  template: '\n    <q-select\n      ref="qRef"\n      :options="filteredOptions"\n      @filter="filterFn"\n      @popup-show="addClass"\n      @popup-hide="removeClass"\n    >\n      <template v-for="(_, slot) in $slots" v-slot:[slot]="slotProps">\n        <slot :name="slot" v-bind="slotProps || {}" />\n      </template>\n    </q-select>\n  ',
  data() {
    return {
      initialOptions: this.options,
      filteredOptions: this.options
    };
  },
  methods: {
    filterFn(val, update, abort) {
      update(() => this.filteredOptions = val ? this.findFilteredOptions() : this.initialOptions);
    },
    findFilteredOptions() {
      var _a;
      const needle = (_a = this.$el.querySelector("input[type=search]")) == null ? void 0 : _a.value.toLocaleLowerCase();
      return needle ? this.initialOptions.filter((v) => String(v.label).toLocaleLowerCase().indexOf(needle) > -1) : this.initialOptions;
    },
    addClass() {
      document.documentElement.classList.add("nicegui-select-popup-open");
    },
    async removeClass() {
      await this.$nextTick();
      document.documentElement.classList.remove("nicegui-select-popup-open");
    }
  },
  updated() {
    if (!this.$attrs.multiple) return;
    const newFilteredOptions = this.findFilteredOptions();
    if (newFilteredOptions.length !== this.filteredOptions.length) {
      this.filteredOptions = newFilteredOptions;
    }
  },
  unmounted() {
    this.removeClass();
  },
  watch: {
    options: {
      handler(newOptions) {
        this.initialOptions = newOptions;
        this.filteredOptions = newOptions;
      },
      immediate: true
    }
  }
};
