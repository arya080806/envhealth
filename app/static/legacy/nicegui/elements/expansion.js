var __getOwnPropSymbols = Object.getOwnPropertySymbols;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __propIsEnum = Object.prototype.propertyIsEnumerable;
var __objRest = (source, exclude) => {
  var target = {};
  for (var prop in source)
    if (__hasOwnProp.call(source, prop) && exclude.indexOf(prop) < 0)
      target[prop] = source[prop];
  if (source != null && __getOwnPropSymbols)
    for (var prop of __getOwnPropSymbols(source)) {
      if (exclude.indexOf(prop) < 0 && __propIsEnum.call(source, prop))
        target[prop] = source[prop];
    }
  return target;
};
export default {
  template: `
    <q-expansion-item ref="qRef">
      <template v-for="(_, name) in nonDefaultSlots" :key="name" v-slot:[name]="slotProps">
        <slot :name="name" v-bind="slotProps || {}" />
      </template>
      <div class="nicegui-expansion-content">
        <slot></slot>
      </div>
    </q-expansion-item>
  `,
  computed: {
    nonDefaultSlots() {
      const _a = this.$slots, { default: _ } = _a, rest = __objRest(_a, ["default"]);
      return rest;
    }
  }
};
