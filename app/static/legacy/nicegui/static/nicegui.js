var _a;
const True = true;
const False = false;
const None = void 0;
let app = void 0;
let mounted_app = void 0;
function initUnoCss() {
  if (window.__unocss_runtime === void 0) return;
  const renderedClasses = /* @__PURE__ */ new Set();
  let queue = Promise.resolve();
  let isInitialized = false;
  new MutationObserver((mutations) => {
    let newClassesString = "";
    function appendClass(className) {
      if (renderedClasses.has(className)) return;
      renderedClasses.add(className);
      newClassesString += className + " ";
    }
    for (const mutation of mutations) {
      if (mutation.type === "attributes") {
        for (const className of mutation.target.classList) appendClass(className);
      } else if (mutation.type === "childList") {
        for (const node of mutation.addedNodes) {
          if (node.nodeType !== Node.ELEMENT_NODE) continue;
          for (const el of [node, ...node.querySelectorAll("*")]) {
            for (const className of el.classList) appendClass(className);
          }
        }
      }
    }
    if (newClassesString.length === 0) return;
    queue = queue.then(async () => {
      await window.__unocss_runtime.extract(newClassesString);
      if (isInitialized) return;
      for (const style of document.querySelectorAll("style[data-unocss-runtime-layer]"))
        document.head.appendChild(style);
      document.getElementById("app").classList.remove("nicegui-unocss-loading");
      isInitialized = true;
    });
  }).observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ["class"] });
}
function applyColors(colors) {
  const quasarColors = [
    "primary",
    "secondary",
    "accent",
    "dark",
    "dark-page",
    "positive",
    "negative",
    "info",
    "warning"
  ];
  let customCSS = "";
  for (let color in colors) {
    if (quasarColors.includes(color)) continue;
    const colorName = color.replaceAll("_", "-");
    const colorVar = "--q-" + colorName;
    document.body.style.setProperty(colorVar, colors[color]);
    customCSS += ".text-".concat(colorName, " { color: var(").concat(colorVar, ") !important; }\n");
    customCSS += ".bg-".concat(colorName, " { background-color: var(").concat(colorVar, ") !important; }\n");
  }
  if (!customCSS) return;
  const style = document.createElement("style");
  style.innerHTML = customCSS;
  style.dataset.niceguiCustomColors = "";
  document.head.querySelectorAll("[data-nicegui-custom-colors]").forEach((el) => el.remove());
  document.getElementsByTagName("head")[0].appendChild(style);
}
let darkSetter = void 0;
function setDark(dark) {
  if (dark === null) dark = None;
  darkSetter == null ? void 0 : darkSetter(dark);
  document.getElementById("nicegui-color-scheme").setAttribute("content", dark === None ? "normal" : dark ? "dark" : "light");
}
function parseElements(raw_elements) {
  return JSON.parse(
    raw_elements.replace(/&#36;/g, "$").replace(/&#96;/g, "`").replace(/&gt;/g, ">").replace(/&lt;/g, "<").replace(/&amp;/g, "&")
  );
}
function replaceUndefinedAttributes(element2) {
  var _a2, _b, _c, _d, _e, _f, _g;
  (_a2 = element2.class) != null ? _a2 : element2.class = [];
  (_b = element2.style) != null ? _b : element2.style = {};
  (_c = element2.props) != null ? _c : element2.props = {};
  (_d = element2.text) != null ? _d : element2.text = null;
  (_e = element2.events) != null ? _e : element2.events = [];
  (_f = element2.update_method) != null ? _f : element2.update_method = null;
  element2.slots = {
    default: { ids: element2.children || [] },
    ...(_g = element2.slots) != null ? _g : {}
  };
}
function getElement(id2) {
  const _id = id2 instanceof Element ? id2.id.slice(1) : id2;
  return mounted_app.$refs["r" + _id];
}
function getHtmlElement(id2) {
  let id_as_a_string = id2.toString();
  if (!id_as_a_string.startsWith("c")) {
    id_as_a_string = "c" + id_as_a_string;
  }
  return document.getElementById(id_as_a_string);
}
function runMethod(target, method_name, args) {
  if (typeof target === "object") {
    if (method_name in target) {
      return target[method_name](...args);
    }
  } else {
    const element2 = getElement(target);
    if (element2 === null || element2 === void 0) return;
    if (method_name in element2) {
      return element2[method_name](...args);
    } else if (method_name in (element2.$refs.qRef || [])) {
      return element2.$refs.qRef[method_name](...args);
    }
  }
  let msg = 'Method "'.concat(method_name, '" not found.');
  if (method_name.includes("=>") || method_name.startsWith("(")) {
    msg += " To run arbitrary JavaScript, use ui.run_javascript() instead.";
  }
  logAndEmit("error", msg);
}
function getComputedProp(target, prop_name) {
  if (typeof target === "object" && prop_name in target) {
    return target[prop_name];
  }
  const element2 = getElement(target);
  if (element2 === null || element2 === void 0) return;
  if (prop_name in element2) {
    return element2[prop_name];
  } else if (prop_name in (element2.$refs.qRef || [])) {
    return element2.$refs.qRef[prop_name];
  }
}
function emitEvent(event_name2, ...args) {
  getElement(0).$emit(event_name2, ...args);
}
function logAndEmit(level, message) {
  if (level === "error") {
    console.error(message);
  } else if (level === "warning") {
    console.warn(message);
  } else {
    console.log(message);
  }
  window.socket.emit("log", { client_id: window.clientId, level, message });
}
function stringifyEventArgs(args, event_args) {
  const result = [];
  args.forEach((arg, i) => {
    if (event_args !== null && i >= event_args.length) return;
    let filtered = {};
    if (typeof arg !== "object" || arg === null || Array.isArray(arg)) {
      filtered = arg;
    } else {
      for (let k in arg) {
        if (k == "originalTarget") {
          try {
            arg[k].toString();
          } catch (e2) {
            continue;
          }
        }
        if (event_args === null || event_args[i] === null || event_args[i].includes(k)) {
          filtered[k] = arg[k];
        }
      }
    }
    result.push(JSON.stringify(filtered, (k, v) => v instanceof Node || v instanceof Window ? void 0 : v));
  });
  return result;
}
const waitingCallbacks = /* @__PURE__ */ new Map();
function throttle(callback, time, leading, trailing, id2) {
  if (time <= 0) {
    callback();
    return;
  }
  if (waitingCallbacks.has(id2)) {
    if (trailing) {
      waitingCallbacks.set(id2, callback);
    }
  } else {
    if (leading) {
      callback();
      waitingCallbacks.set(id2, null);
    } else if (trailing) {
      waitingCallbacks.set(id2, callback);
    }
    if (leading || trailing) {
      setTimeout(() => {
        const trailingCallback = waitingCallbacks.get(id2);
        if (trailingCallback) trailingCallback();
        waitingCallbacks.delete(id2);
      }, 1e3 * time);
    }
  }
}
function renderRecursively(elements, id, propsContext) {
  const element = elements[id];
  if (element === void 0) {
    return;
  }
  const props = {
    id: "c" + id,
    ref: "r" + id,
    key: id,
    // HACK: workaround for #600 and #898
    class: element.class.join(" ") || void 0,
    style: Object.entries(element.style).reduce((str, [p, val]) => "".concat(str).concat(p, ":").concat(val, ";"), "") || void 0,
    ...element.props
  };
  Object.entries(props).forEach(([key, value]) => {
    if (key.startsWith(":")) {
      try {
        try {
          props[key.substring(1)] = new Function("props", "return (".concat(value, ")"))(propsContext);
        } catch (e) {
          props[key.substring(1)] = eval(value);
        }
        delete props[key];
      } catch (e2) {
        console.error("Error while converting ".concat(key, " attribute to function:"), e2);
      }
    }
  });
  element.events.forEach((event) => {
    let event_name = "on" + event.type[0].toLocaleUpperCase() + event.type.substring(1);
    event.specials.forEach((s) => event_name += s[0].toLocaleUpperCase() + s.substring(1));
    const emit = (...args) => {
      const emitter = () => {
        var _a2;
        return (_a2 = window.socket) == null ? void 0 : _a2.emit("event", {
          id,
          client_id: window.clientId,
          listener_id: event.listener_id,
          args: stringifyEventArgs(args, event.args)
        });
      };
      const delayed_emitter = () => {
        if (window.did_handshake) emitter();
        else setTimeout(delayed_emitter, 10);
      };
      throttle(delayed_emitter, event.throttle, event.leading_events, event.trailing_events, event.listener_id);
      if (element.props["loopback"] === False && event.type == "update:modelValue") {
        element.props["model-value"] = args;
      }
    };
    let handler;
    if (event.js_handler) {
      const props = propsContext;
      handler = eval(event.js_handler);
    } else {
      handler = emit;
    }
    handler = Vue.withModifiers(handler, event.modifiers);
    handler = event.keys.length ? Vue.withKeys(handler, event.keys) : handler;
    if (props[event_name]) {
      props[event_name].push(handler);
    } else {
      props[event_name] = [handler];
    }
  });
  const slots = {};
  const element_slots = {
    default: { ids: element.children || [] },
    ...element.slots
  };
  Object.entries(element_slots).forEach(([name, data]) => {
    slots[name] = (props2) => {
      const rendered = [];
      if (data.template) {
        rendered.push(
          Vue.h(
            {
              props: { props: { type: Object, default: {} } },
              template: data.template
            },
            {
              props: props2
            }
          )
        );
      }
      const children = data.ids.map((id2) => renderRecursively(elements, id2, props2 || propsContext));
      if (name === "default" && element.text !== null) {
        children.unshift(element.text);
      }
      return [...rendered, ...children];
    };
  });
  return Vue.h(app.config.isNativeTag(element.tag) ? element.tag : Vue.resolveComponent(element.tag), props, slots);
}
function runJavascript(code, request_id) {
  new Promise((resolve) => resolve(eval(code))).catch((reason) => {
    if (reason instanceof SyntaxError) return eval("(async() => {".concat(code, "})()"));
    else throw reason;
  }).then((result) => {
    if (request_id) {
      window.socket.emit("javascript_response", { request_id, client_id: window.clientId, result });
    }
  });
}
function download(src, filename, mediaType, prefix) {
  const anchor = document.createElement("a");
  if (typeof src === "string") {
    anchor.href = src.startsWith("/") ? prefix + src : src;
  } else {
    anchor.href = URL.createObjectURL(new Blob([src], { type: mediaType }));
  }
  anchor.target = "_blank";
  anchor.download = filename || "";
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  if (typeof src !== "string") {
    URL.revokeObjectURL(anchor.href);
  }
}
function ack() {
  if (!window.socket || !window.did_handshake) return;
  if (window.ackedMessageId >= window.nextMessageId) return;
  window.socket.emit("ack", {
    client_id: window.clientId,
    next_message_id: window.nextMessageId
  });
  window.ackedMessageId = window.nextMessageId;
}
function createRandomUUID() {
  try {
    return crypto.randomUUID();
  } catch (e2) {
    return "10000000-1000-4000-8000-100000000000".replace(
      /[018]/g,
      (c) => (+c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> +c / 4).toString(16)
    );
  }
}
const OLD_TAB_ID = sessionStorage.__nicegui_tab_closed === "false" ? sessionStorage.__nicegui_tab_id : null;
const TAB_ID = !sessionStorage.__nicegui_tab_id || sessionStorage.__nicegui_tab_closed === "false" ? sessionStorage.__nicegui_tab_id = createRandomUUID() : sessionStorage.__nicegui_tab_id;
sessionStorage.__nicegui_tab_closed = "false";
window.onbeforeunload = function() {
  sessionStorage.__nicegui_tab_closed = "true";
};
function createApp(elements2, options) {
  Object.entries(elements2).forEach(([_, element2]) => replaceUndefinedAttributes(element2));
  setInterval(() => ack(), 3e3);
  initUnoCss();
  return app = Vue.createApp({
    data() {
      return {
        elements: elements2
      };
    },
    render() {
      return renderRecursively(this.elements, 0);
    },
    mounted() {
      mounted_app = this;
      window.documentId = createRandomUUID();
      window.clientId = options.query.client_id;
      const url = (window.location.protocol === "https:" ? "wss://" : "ws://") + window.location.host;
      window.path_prefix = options.prefix;
      window.nextMessageId = options.query.next_message_id;
      window.ackedMessageId = -1;
      options.query.document_id = window.documentId;
      options.query.tab_id = TAB_ID;
      options.query.old_tab_id = OLD_TAB_ID;
      window.socket = io(url, {
        path: "".concat(options.prefix, "/_nicegui_ws/socket.io"),
        query: options.query,
        extraHeaders: options.extraHeaders,
        transports: "prerendering" in document && document.prerendering === true ? ["polling", ...options.transports] : options.transports
      });
      window.did_handshake = false;
      const messageHandlers = {
        connect: () => {
          var _a2;
          function wrapFunction(originalFunction) {
            const MAX_WEBSOCKET_MESSAGE_SIZE = 1e6 - 100;
            return function(...args) {
              const msg = args[0];
              if (typeof msg === "string" && msg.length > MAX_WEBSOCKET_MESSAGE_SIZE) {
                const errorMessage = "Payload size ".concat(msg.length, " exceeds the maximum allowed limit.");
                console.error(errorMessage);
                args[0] = '42["log",{"client_id":"'.concat(window.clientId, '","level":"error","message":"').concat(errorMessage, '"}]');
                if (window.tooLongMessageTimerId) clearTimeout(window.tooLongMessageTimerId);
                const popup = document.getElementById("too_long_message_popup");
                popup.ariaHidden = false;
                window.tooLongMessageTimerId = setTimeout(() => popup.ariaHidden = true, 5e3);
              }
              return originalFunction.call(this, ...args);
            };
          }
          const transport = window.socket.io.engine.transport;
          if ((_a2 = transport == null ? void 0 : transport.ws) == null ? void 0 : _a2.send) transport.ws.send = wrapFunction(transport.ws.send);
          if (transport == null ? void 0 : transport.doWrite) transport.doWrite = wrapFunction(transport.doWrite);
          function finishHandshake(ok) {
            if (!ok) {
              console.log("reloading because handshake failed for clientId " + window.clientId);
              window.location.reload();
            }
            window.did_handshake = true;
            document.getElementById("popup").ariaHidden = true;
          }
          if (options.query.implicit_handshake) {
            finishHandshake(true);
          } else {
            window.socket.emit("handshake", options.query, finishHandshake);
          }
        },
        connect_error: (err) => {
          if (err.message == "timeout") {
            console.log("reloading because connection timed out");
            window.location.reload();
          } else if (err.message == "Implicit handshake failed") {
            console.log("reloading because implicit handshake failed for clientId " + window.clientId);
            window.location.reload();
          }
        },
        try_reconnect: async () => {
          document.getElementById("popup").ariaHidden = false;
          await fetch(window.location.href, { headers: { "NiceGUI-Check": "try_reconnect" } });
          console.log("reloading because reconnect was requested");
          window.location.reload();
        },
        disconnect: () => {
          document.getElementById("popup").ariaHidden = false;
        },
        load_js_components: async (msg) => {
          const urls = msg.components.map((c) => "".concat(options.prefix, "/_nicegui/").concat(options.version, "/components/").concat(c.key));
          const imports = await Promise.all(urls.map((url2) => import(url2)));
          msg.components.forEach((c, i) => app.component(c.tag, imports[i].default));
        },
        update: async (msg) => {
          var _a2, _b, _c;
          let eventListenersChanged = false;
          for (const [id2, element2] of Object.entries(msg)) {
            if (element2 === null) continue;
            if (!(id2 in this.elements)) continue;
            const oldListenerIds = new Set((((_a2 = this.elements[id2]) == null ? void 0 : _a2.events) || []).map((ev) => ev.listener_id));
            if ((_b = element2.events) == null ? void 0 : _b.some((e2) => !oldListenerIds.has(e2.listener_id))) {
              delete this.elements[id2];
              eventListenersChanged = true;
            }
          }
          if (eventListenersChanged) {
            logAndEmit("warning", "Event listeners changed after initial definition. Re-rendering affected elements.");
            await this.$nextTick();
          }
          for (const [id2, element2] of Object.entries(msg)) {
            if (element2 === null) {
              delete this.elements[id2];
              continue;
            }
            replaceUndefinedAttributes(element2);
            this.elements[id2] = element2;
          }
          await this.$nextTick();
          for (const [id2, element2] of Object.entries(msg)) {
            if (element2 == null ? void 0 : element2.update_method) {
              (_c = getElement(id2)) == null ? void 0 : _c[element2.update_method]();
            }
          }
        },
        run_javascript: (msg) => runJavascript(msg.code, msg.request_id),
        open: (msg) => {
          const url2 = msg.path.startsWith("/") ? options.prefix + msg.path : msg.path;
          const target = msg.new_tab ? "_blank" : "_self";
          window.open(url2, target);
        },
        download: (msg) => download(msg.src, msg.filename, msg.media_type, options.prefix),
        notify: (msg) => Quasar.Notify.create(msg)
      };
      const socketMessageQueue = [];
      let isProcessingSocketMessage = false;
      for (const [event2, handler2] of Object.entries(messageHandlers)) {
        window.socket.on(event2, async (...args) => {
          if (args.length > 0 && args[0]._id !== void 0) {
            const message_id = args[0]._id;
            if (message_id < window.nextMessageId) return;
            window.nextMessageId = message_id + 1;
            delete args[0]._id;
          }
          socketMessageQueue.push(() => handler2(...args));
          if (!isProcessingSocketMessage) {
            while (socketMessageQueue.length > 0) {
              const handler3 = socketMessageQueue.shift();
              isProcessingSocketMessage = true;
              try {
                await handler3();
              } catch (e2) {
                console.error(e2);
              }
              isProcessingSocketMessage = false;
            }
          }
        });
      }
    }
  });
}
for (const importRule of document.styleSheets[0].cssRules) {
  if (importRule instanceof CSSImportRule && /quasar/.test((_a = importRule.styleSheet) == null ? void 0 : _a.href)) {
    for (const rule of Array.from(importRule.styleSheet.cssRules)) {
      if (rule instanceof CSSStyleRule && /\.q-card > div/.test(rule.selectorText)) {
        if (/\.q-card > div/.test(rule.selectorText)) rule.selectorText = ".nicegui-card-tight" + rule.selectorText;
      }
    }
  }
}
