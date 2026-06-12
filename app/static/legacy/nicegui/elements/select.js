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
  props: ["options"],
  template: `
    <q-select
      ref="qRef"
      :options="filteredOptions"
      @filter="filterFn"
      @popup-show="addClass"
      @popup-hide="removeClass"
    >
      <template v-for="(_, slot) in $slots" v-slot:[slot]="slotProps">
        <slot :name="slot" v-bind="slotProps || {}" />
      </template>
    </q-select>
  `,
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
    removeClass() {
      return __async(this, null, function* () {
        yield this.$nextTick();
        document.documentElement.classList.remove("nicegui-select-popup-open");
      });
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
