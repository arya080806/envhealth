export default {
  template: '\n    <q-editor ref="qRef" :id="id" v-model="inputValue">\n      <template v-for="(_, slot) in $slots" v-slot:[slot]="slotProps">\n        <slot :name="slot" v-bind="slotProps || {}" />\n      </template>\n    </q-editor>\n  ',
  props: {
    value: String,
    id: String
  },
  data() {
    return {
      inputValue: this.value,
      emitting: true
    };
  },
  beforeUnmount() {
    const element = mounted_app.elements[this.$props.id.slice(1)];
    if (element) element.props.value = this.inputValue;
  },
  watch: {
    value(newValue) {
      this.emitting = false;
      this.inputValue = newValue;
      this.$nextTick(() => this.emitting = true);
    },
    inputValue(newValue) {
      if (!this.emitting) return;
      this.$emit("update:value", newValue);
    }
  },
  methods: {
    updateValue() {
      this.inputValue = this.value;
    }
  }
};
