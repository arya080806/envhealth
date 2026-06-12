var __defProp = Object.defineProperty;
var __getOwnPropSymbols = Object.getOwnPropertySymbols;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __propIsEnum = Object.prototype.propertyIsEnumerable;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __spreadValues = (a, b) => {
  for (var prop in b || (b = {}))
    if (__hasOwnProp.call(b, prop))
      __defNormalProp(a, prop, b[prop]);
  if (__getOwnPropSymbols)
    for (var prop of __getOwnPropSymbols(b)) {
      if (__propIsEnum.call(b, prop))
        __defNormalProp(a, prop, b[prop]);
    }
  return a;
};
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
import { load_widget, load_css } from "widget";
import { cleanObject } from "../../static/utils/json.js";
export default {
  template: "<div></div>",
  mounted() {
    return __async(this, null, function* () {
      var _a, _b;
      const emit_to_py = this.$emit;
      this.model = {
        attributes: __spreadValues({}, this.traits),
        callbacks: {},
        get: function(key) {
          return cleanObject(this.attributes[key]);
        },
        set: function(key, value) {
          this.attributes[key] = value;
          this.emit("change:" + key, value);
        },
        save_changes: function() {
          if (this.callbacks.change && Array.isArray(this.callbacks.change)) {
            this.callbacks.change.forEach((cb) => cb());
          }
          emit_to_py("update:traits", __spreadValues({}, this.attributes));
        },
        on: function(event, callback) {
          if (!this.callbacks[event]) this.callbacks[event] = [];
          this.callbacks[event].push(callback);
        },
        off: function(event, callback) {
          var _a2;
          if (!event) this.callbacks = {};
          else if (!callback) this.callbacks[event] = [];
          else (_a2 = this.callbacks[event]) == null ? void 0 : _a2.delete(callback);
        },
        emit: function(event, value) {
          var _a2;
          (_a2 = this.callbacks[event]) == null ? void 0 : _a2.forEach((cb) => cb(value));
        },
        send: function(content, callbacks, buffers) {
          console.warn("anywidget.send() is not yet implemented in NiceGUI", content);
        }
      };
      const mod = yield load_widget(this.esm_content, this.traits._anywidget_id);
      this.cleanup_widget = yield (_a = mod.initialize) == null ? void 0 : _a.call(mod, { model: this.model });
      this.cleanup_view = yield (_b = mod.render) == null ? void 0 : _b.call(mod, { model: this.model, el: this.$el });
      load_css(this.css_content, this.traits._anywidget_id);
    });
  },
  methods: {
    update_trait(trait, value) {
      this.model.set(trait, value);
    }
  },
  props: {
    traits: Object,
    esm_content: String,
    css_content: String
  }
};
