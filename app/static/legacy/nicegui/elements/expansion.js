export default {
  template: '\n    <q-expansion-item ref="qRef">\n      <template v-for="(_, name) in nonDefaultSlots" :key="name" v-slot:[name]="slotProps">\n        <slot :name="name" v-bind="slotProps || {}" />\n      </template>\n      <div class="nicegui-expansion-content">\n        <slot></slot>\n      </div>\n    </q-expansion-item>\n  ',
  computed: {
    nonDefaultSlots() {
      const { default: _, ...rest } = this.$slots;
      return rest;
    }
  }
};
