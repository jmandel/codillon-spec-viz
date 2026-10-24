function __wbg_get_imports() {
    const import0 = {
        __proto__: null,
        __wbg___wbindgen_debug_string_c25d447a39f5578f: function(arg0, arg1) {
            const ret = debugString(arg1);
            const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg___wbindgen_is_function_1ff95bcc5517c252: function(arg0) {
            const ret = typeof(arg0) === 'function';
            return ret;
        },
        __wbg___wbindgen_is_undefined_c05833b95a3cf397: function(arg0) {
            const ret = arg0 === undefined;
            return ret;
        },
        __wbg___wbindgen_string_get_b0ca35b86a603356: function(arg0, arg1) {
            const obj = arg1;
            const ret = typeof(obj) === 'string' ? obj : undefined;
            var ptr1 = isLikeNone(ret) ? 0 : passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            var len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg___wbindgen_throw_344f42d3211c4765: function(arg0, arg1) {
            throw new Error(getStringFromWasm0(arg0, arg1));
        },
        __wbg__wbg_cb_unref_fffb441def202758: function(arg0) {
            arg0._wbg_cb_unref();
        },
        __wbg_add_38cee25662852903: function() { return handleError(function (arg0, arg1, arg2) {
            arg0.add(getStringFromWasm0(arg1, arg2));
        }, arguments); },
        __wbg_anchorNode_0b9dce0698d0f60a: function(arg0) {
            const ret = arg0.anchorNode;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_anchorOffset_ef209834359b4acb: function(arg0) {
            const ret = arg0.anchorOffset;
            return ret;
        },
        __wbg_appendChild_f553e8704c4f14a6: function() { return handleError(function (arg0, arg1) {
            const ret = arg0.appendChild(arg1);
            return ret;
        }, arguments); },
        __wbg_appendData_61aeddceb1986cad: function() { return handleError(function (arg0, arg1, arg2) {
            arg0.appendData(getStringFromWasm0(arg1, arg2));
        }, arguments); },
        __wbg_append_6c3c5a4e89d0c763: function() { return handleError(function (arg0, arg1) {
            arg0.append(arg1);
        }, arguments); },
        __wbg_apply_3ac86a26fdb56c05: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.apply(arg1, arg2);
            return ret;
        }, arguments); },
        __wbg_arc_61372d0a8f0a988c: function() { return handleError(function (arg0, arg1, arg2, arg3, arg4, arg5) {
            arg0.arc(arg1, arg2, arg3, arg4, arg5);
        }, arguments); },
        __wbg_beginPath_ca2dfce389ff20d2: function(arg0) {
            arg0.beginPath();
        },
        __wbg_body_40ec34e0a2931fe8: function(arg0) {
            const ret = arg0.body;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_checked_596d0d7b35f55a01: function(arg0) {
            const ret = arg0.checked;
            return ret;
        },
        __wbg_childNodes_c4fcb612cf4b6de1: function(arg0) {
            const ret = arg0.childNodes;
            return ret;
        },
        __wbg_classList_8c12288eeff7eadb: function(arg0) {
            const ret = arg0.classList;
            return ret;
        },
        __wbg_clearRect_520d2bbc2437bfaa: function(arg0, arg1, arg2, arg3, arg4) {
            arg0.clearRect(arg1, arg2, arg3, arg4);
        },
        __wbg_clipboard_cc7335fcba1a9a80: function(arg0) {
            const ret = arg0.clipboard;
            return ret;
        },
        __wbg_closest_d889c758da4bb13b: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.closest(getStringFromWasm0(arg1, arg2));
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        }, arguments); },
        __wbg_compareDocumentPosition_2396436dc1fc2727: function(arg0, arg1) {
            const ret = arg0.compareDocumentPosition(arg1);
            return ret;
        },
        __wbg_createElementNS_013b3fb26f4796ec: function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
            const ret = arg0.createElementNS(arg1 === 0 ? undefined : getStringFromWasm0(arg1, arg2), getStringFromWasm0(arg3, arg4));
            return ret;
        }, arguments); },
        __wbg_createElement_fcbc0805de826d62: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.createElement(getStringFromWasm0(arg1, arg2));
            return ret;
        }, arguments); },
        __wbg_ctrlKey_2e52816fa7160097: function(arg0) {
            const ret = arg0.ctrlKey;
            return ret;
        },
        __wbg_dataTransfer_6d423aa33da05b8f: function(arg0) {
            const ret = arg0.dataTransfer;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_data_a0edd0cabddb5e65: function(arg0, arg1) {
            const ret = arg1.data;
            var ptr1 = isLikeNone(ret) ? 0 : passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            var len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg_document_179650d6cb13c263: function(arg0) {
            const ret = arg0.document;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_endContainer_9c9077583ab06e9b: function() { return handleError(function (arg0) {
            const ret = arg0.endContainer;
            return ret;
        }, arguments); },
        __wbg_endOffset_b936d7b056475532: function() { return handleError(function (arg0) {
            const ret = arg0.endOffset;
            return ret;
        }, arguments); },
        __wbg_error_a6fa202b58aa1cd3: function(arg0, arg1) {
            let deferred0_0;
            let deferred0_1;
            try {
                deferred0_0 = arg0;
                deferred0_1 = arg1;
                console.error(getStringFromWasm0(arg0, arg1));
            } finally {
                wasm.__wbindgen_free(deferred0_0, deferred0_1, 1);
            }
        },
        __wbg_fetch_58167e2c1ef32e0a: function(arg0, arg1, arg2) {
            const ret = arg0.fetch(getStringFromWasm0(arg1, arg2));
            return ret;
        },
        __wbg_fetch_b3cd62fa355e25fd: function(arg0, arg1, arg2, arg3) {
            const ret = arg0.fetch(getStringFromWasm0(arg1, arg2), arg3);
            return ret;
        },
        __wbg_fill_7e2406c195723006: function(arg0) {
            arg0.fill();
        },
        __wbg_focusNode_25301a7620bd15e3: function(arg0) {
            const ret = arg0.focusNode;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_focusOffset_89613f20e6ed3303: function(arg0) {
            const ret = arg0.focusOffset;
            return ret;
        },
        __wbg_getAttribute_5a601ba4718b922a: function(arg0, arg1, arg2, arg3) {
            const ret = arg1.getAttribute(getStringFromWasm0(arg2, arg3));
            var ptr1 = isLikeNone(ret) ? 0 : passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            var len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg_getBoundingClientRect_e828e6c31c66dea6: function(arg0) {
            const ret = arg0.getBoundingClientRect();
            return ret;
        },
        __wbg_getContext_e79ddf6a9cb3cc76: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.getContext(getStringFromWasm0(arg1, arg2));
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        }, arguments); },
        __wbg_getData_fcb88fae21d94f1e: function() { return handleError(function (arg0, arg1, arg2, arg3) {
            const ret = arg1.getData(getStringFromWasm0(arg2, arg3));
            const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        }, arguments); },
        __wbg_getElementById_1cbd8f06dbe8eb8e: function(arg0, arg1, arg2) {
            const ret = arg0.getElementById(getStringFromWasm0(arg1, arg2));
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_getItem_b96269ddc16cf24a: function() { return handleError(function (arg0, arg1, arg2, arg3) {
            const ret = arg1.getItem(getStringFromWasm0(arg2, arg3));
            var ptr1 = isLikeNone(ret) ? 0 : passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            var len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        }, arguments); },
        __wbg_getSelection_5d3a5a6e5b6a1ddd: function() { return handleError(function (arg0) {
            const ret = arg0.getSelection();
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        }, arguments); },
        __wbg_getTargetRanges_f997de0a598ad50c: function(arg0) {
            const ret = arg0.getTargetRanges();
            return ret;
        },
        __wbg_get_507a50627bffa49b: function(arg0, arg1) {
            const ret = arg0[arg1 >>> 0];
            return ret;
        },
        __wbg_get_78f252d074a84d0b: function() { return handleError(function (arg0, arg1) {
            const ret = Reflect.get(arg0, arg1);
            return ret;
        }, arguments); },
        __wbg_hash_508149c4291ec8c2: function() { return handleError(function (arg0, arg1) {
            const ret = arg1.hash;
            const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        }, arguments); },
        __wbg_href_0259f7f614252f13: function() { return handleError(function (arg0, arg1) {
            const ret = arg1.href;
            const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        }, arguments); },
        __wbg_inputType_37c59110203135d8: function(arg0, arg1) {
            const ret = arg1.inputType;
            const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg_insertBefore_9121f73148bc4f7c: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.insertBefore(arg1, arg2);
            return ret;
        }, arguments); },
        __wbg_instanceof_CanvasRenderingContext2d_2284b703b7023dcc: function(arg0) {
            let result;
            try {
                result = arg0 instanceof CanvasRenderingContext2D;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_Element_beebfaab75d12d9d: function(arg0) {
            let result;
            try {
                result = arg0 instanceof Element;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_HtmlBodyElement_3283b347a2e6a480: function(arg0) {
            let result;
            try {
                result = arg0 instanceof HTMLBodyElement;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_HtmlBrElement_1374e9b3a32ec306: function(arg0) {
            let result;
            try {
                result = arg0 instanceof HTMLBRElement;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_HtmlCanvasElement_ed02ed9136056019: function(arg0) {
            let result;
            try {
                result = arg0 instanceof HTMLCanvasElement;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_HtmlDivElement_a66705e5e9d2ac14: function(arg0) {
            let result;
            try {
                result = arg0 instanceof HTMLDivElement;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_HtmlInputElement_ad3be04339d0e4df: function(arg0) {
            let result;
            try {
                result = arg0 instanceof HTMLInputElement;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_HtmlSpanElement_73299c916b1d269f: function(arg0) {
            let result;
            try {
                result = arg0 instanceof HTMLSpanElement;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_Response_c8b64b2256f01bec: function(arg0) {
            let result;
            try {
                result = arg0 instanceof Response;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_RuntimeError_fa0d96398e97d301: function(arg0) {
            let result;
            try {
                result = arg0 instanceof WebAssembly.RuntimeError;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_SvgDefsElement_70362733b216c639: function(arg0) {
            let result;
            try {
                result = arg0 instanceof SVGDefsElement;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_SvgElement_c4bca0a00964b694: function(arg0) {
            let result;
            try {
                result = arg0 instanceof SVGElement;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_SvgLinearGradientElement_0acd3f4ca04982d6: function(arg0) {
            let result;
            try {
                result = arg0 instanceof SVGLinearGradientElement;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_SvgMaskElement_3c1a9fcae8efb698: function(arg0) {
            let result;
            try {
                result = arg0 instanceof SVGMaskElement;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_SvgPathElement_9acbd53552489a55: function(arg0) {
            let result;
            try {
                result = arg0 instanceof SVGPathElement;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_SvgStopElement_b625fff77eb9d2ee: function(arg0) {
            let result;
            try {
                result = arg0 instanceof SVGStopElement;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_SvgTextElement_3b947e0558c0f951: function(arg0) {
            let result;
            try {
                result = arg0 instanceof SVGTextElement;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_SvgUseElement_938a1b9ab52c5ff8: function(arg0) {
            let result;
            try {
                result = arg0 instanceof SVGUseElement;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_SvggElement_a215c5086abec3a1: function(arg0) {
            let result;
            try {
                result = arg0 instanceof SVGGElement;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_Window_05ba1ee4f6781663: function(arg0) {
            let result;
            try {
                result = arg0 instanceof Window;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instantiate_222cb1650e0759e1: function(arg0, arg1, arg2) {
            const ret = WebAssembly.instantiate(getArrayU8FromWasm0(arg0, arg1), arg2);
            return ret;
        },
        __wbg_isCollapsed_317d94bbdd63194c: function(arg0) {
            const ret = arg0.isCollapsed;
            return ret;
        },
        __wbg_isConnected_c24b5a7bb035eae0: function(arg0) {
            const ret = arg0.isConnected;
            return ret;
        },
        __wbg_isSameNode_75a8a5f6302c6182: function(arg0, arg1) {
            const ret = arg0.isSameNode(arg1);
            return ret;
        },
        __wbg_item_20d060e2ba81115e: function(arg0, arg1) {
            const ret = arg0.item(arg1 >>> 0);
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_key_803dca86cdcfa8dd: function(arg0, arg1) {
            const ret = arg1.key;
            const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg_length_1f0964f4a5e2c6d8: function(arg0) {
            const ret = arg0.length;
            return ret;
        },
        __wbg_length_370319915dc99107: function(arg0) {
            const ret = arg0.length;
            return ret;
        },
        __wbg_localStorage_5bf6ce3f8e51412a: function() { return handleError(function (arg0) {
            const ret = arg0.localStorage;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        }, arguments); },
        __wbg_location_c9a2271428996698: function(arg0) {
            const ret = arg0.location;
            return ret;
        },
        __wbg_log_d267660666346fb3: function(arg0) {
            console.log(arg0);
        },
        __wbg_measureText_c54a480a20a73a31: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.measureText(getStringFromWasm0(arg1, arg2));
            return ret;
        }, arguments); },
        __wbg_message_8326fb1d549bebc5: function(arg0) {
            const ret = arg0.message;
            return ret;
        },
        __wbg_metaKey_d961c7572a9f84f5: function(arg0) {
            const ret = arg0.metaKey;
            return ret;
        },
        __wbg_navigator_99621db14b3f1099: function(arg0) {
            const ret = arg0.navigator;
            return ret;
        },
        __wbg_new_227d7c05414eb861: function() {
            const ret = new Error();
            return ret;
        },
        __wbg_new_32b398fb48b6d94a: function() {
            const ret = new Array();
            return ret;
        },
        __wbg_new_927fb454d7fb186d: function() { return handleError(function () {
            const ret = new Text();
            return ret;
        }, arguments); },
        __wbg_new_cd45aabdf6073e84: function(arg0) {
            const ret = new Uint8Array(arg0);
            return ret;
        },
        __wbg_new_da52cf8fe3429cb2: function() {
            const ret = new Object();
            return ret;
        },
        __wbg_new_with_length_f8cbc3a5b9ff9368: function(arg0) {
            const ret = new Array(arg0 >>> 0);
            return ret;
        },
        __wbg_now_390768da5ee9e776: function(arg0) {
            const ret = arg0.now();
            return ret;
        },
        __wbg_ok_acc5e3fb89668864: function(arg0) {
            const ret = arg0.ok;
            return ret;
        },
        __wbg_open_221b279749ba2e4e: function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
            const ret = arg0.open(getStringFromWasm0(arg1, arg2), getStringFromWasm0(arg3, arg4));
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        }, arguments); },
        __wbg_parentNode_fecbbdea2a930547: function(arg0) {
            const ret = arg0.parentNode;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_performance_3ef602e13d6c3b56: function(arg0) {
            const ret = arg0.performance;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_preventDefault_b64888c857500682: function(arg0) {
            arg0.preventDefault();
        },
        __wbg_prototypesetcall_4770620bbe4688a0: function(arg0, arg1, arg2) {
            Uint8Array.prototype.set.call(getArrayU8FromWasm0(arg0, arg1), arg2);
        },
        __wbg_push_d2ae3af0c1217ae6: function(arg0, arg1) {
            const ret = arg0.push(arg1);
            return ret;
        },
        __wbg_querySelectorAll_7e98cbe256deaadd: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.querySelectorAll(getStringFromWasm0(arg1, arg2));
            return ret;
        }, arguments); },
        __wbg_querySelector_fd7d157ebe17cd16: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.querySelector(getStringFromWasm0(arg1, arg2));
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        }, arguments); },
        __wbg_queueMicrotask_0ab5b2d2393e99b9: function(arg0) {
            const ret = arg0.queueMicrotask;
            return ret;
        },
        __wbg_queueMicrotask_6a09b7bc46549209: function(arg0) {
            queueMicrotask(arg0);
        },
        __wbg_removeAttribute_1e7d2c409776d836: function() { return handleError(function (arg0, arg1, arg2) {
            arg0.removeAttribute(getStringFromWasm0(arg1, arg2));
        }, arguments); },
        __wbg_removeChild_8d9536328d674d54: function() { return handleError(function (arg0, arg1) {
            const ret = arg0.removeChild(arg1);
            return ret;
        }, arguments); },
        __wbg_removeItem_78e03a38da96e0ae: function() { return handleError(function (arg0, arg1, arg2) {
            arg0.removeItem(getStringFromWasm0(arg1, arg2));
        }, arguments); },
        __wbg_remove_281d6b5594fade8f: function() { return handleError(function (arg0, arg1, arg2) {
            arg0.remove(getStringFromWasm0(arg1, arg2));
        }, arguments); },
        __wbg_remove_ce1b54059317fe8a: function(arg0) {
            arg0.remove();
        },
        __wbg_replaceChild_c6b6b965cc8b9870: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.replaceChild(arg1, arg2);
            return ret;
        }, arguments); },
        __wbg_replaceChildren_cab14dffb646538a: function(arg0, arg1) {
            arg0.replaceChildren(...arg1);
        },
        __wbg_replaceData_c43d914fa9596e08: function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
            arg0.replaceData(arg1 >>> 0, arg2 >>> 0, getStringFromWasm0(arg3, arg4));
        }, arguments); },
        __wbg_requestAnimationFrame_1a85deeab66448c2: function() { return handleError(function (arg0, arg1) {
            const ret = arg0.requestAnimationFrame(arg1);
            return ret;
        }, arguments); },
        __wbg_resolve_2191a4dfe481c25b: function(arg0) {
            const ret = Promise.resolve(arg0);
            return ret;
        },
        __wbg_right_36c53e00496f4f0a: function(arg0) {
            const ret = arg0.right;
            return ret;
        },
        __wbg_scrollIntoView_d8b806f471b7418e: function(arg0, arg1) {
            arg0.scrollIntoView(arg1);
        },
        __wbg_setAttribute_71039043be82d098: function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
            arg0.setAttribute(getStringFromWasm0(arg1, arg2), getStringFromWasm0(arg3, arg4));
        }, arguments); },
        __wbg_setBaseAndExtent_3fc8ef4a2a8807e2: function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
            arg0.setBaseAndExtent(arg1, arg2 >>> 0, arg3, arg4 >>> 0);
        }, arguments); },
        __wbg_setItem_364a11cf21db9039: function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
            arg0.setItem(getStringFromWasm0(arg1, arg2), getStringFromWasm0(arg3, arg4));
        }, arguments); },
        __wbg_setTimeout_cfa2cf195c3738db: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.setTimeout(arg1, arg2);
            return ret;
        }, arguments); },
        __wbg_set_8535240470bf2500: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = Reflect.set(arg0, arg1, arg2);
            return ret;
        }, arguments); },
        __wbg_set_8a16b38e4805b298: function(arg0, arg1, arg2) {
            arg0[arg1 >>> 0] = arg2;
        },
        __wbg_set_behavior_af2ac621388b739f: function(arg0, arg1) {
            arg0.behavior = __wbindgen_enum_ScrollBehavior[arg1];
        },
        __wbg_set_block_8135b3acafa1ca88: function(arg0, arg1) {
            arg0.block = __wbindgen_enum_ScrollLogicalPosition[arg1];
        },
        __wbg_set_body_029f2d171e0a005f: function(arg0, arg1) {
            arg0.body = arg1;
        },
        __wbg_set_body_25d297731d0c1f4d: function(arg0, arg1) {
            arg0.body = arg1;
        },
        __wbg_set_className_e0b1e805ac9ecbf4: function(arg0, arg1, arg2) {
            arg0.className = getStringFromWasm0(arg1, arg2);
        },
        __wbg_set_data_432d97a82587ad29: function(arg0, arg1, arg2) {
            arg0.data = getStringFromWasm0(arg1, arg2);
        },
        __wbg_set_fillStyle_4360b989b9352bbb: function(arg0, arg1, arg2) {
            arg0.fillStyle = getStringFromWasm0(arg1, arg2);
        },
        __wbg_set_font_33fee74f2c82cb6f: function(arg0, arg1, arg2) {
            arg0.font = getStringFromWasm0(arg1, arg2);
        },
        __wbg_set_headers_9c61d123c3ee1f10: function(arg0, arg1) {
            arg0.headers = arg1;
        },
        __wbg_set_id_4beae8b813c092d8: function(arg0, arg1, arg2) {
            arg0.id = getStringFromWasm0(arg1, arg2);
        },
        __wbg_set_innerHTML_f78a45a07f97e136: function(arg0, arg1, arg2) {
            arg0.innerHTML = getStringFromWasm0(arg1, arg2);
        },
        __wbg_set_innerText_847403b9d4f38f77: function(arg0, arg1, arg2) {
            arg0.innerText = getStringFromWasm0(arg1, arg2);
        },
        __wbg_set_method_5532d59b92d76467: function(arg0, arg1, arg2) {
            arg0.method = getStringFromWasm0(arg1, arg2);
        },
        __wbg_set_onbeforeinput_987dd31803e726a4: function(arg0, arg1) {
            arg0.onbeforeinput = arg1;
        },
        __wbg_set_onbeforeunload_a667661666e6f394: function(arg0, arg1) {
            arg0.onbeforeunload = arg1;
        },
        __wbg_set_onclick_527135192dd54d92: function(arg0, arg1) {
            arg0.onclick = arg1;
        },
        __wbg_set_onhashchange_c8bdf9d21b0843f7: function(arg0, arg1) {
            arg0.onhashchange = arg1;
        },
        __wbg_set_oninput_092fb4ed663eb75a: function(arg0, arg1) {
            arg0.oninput = arg1;
        },
        __wbg_set_onkeydown_a58060942a95bfb1: function(arg0, arg1) {
            arg0.onkeydown = arg1;
        },
        __wbg_set_onmousedown_24d4191fe4a460b0: function(arg0, arg1) {
            arg0.onmousedown = arg1;
        },
        __wbg_set_title_4856546ac7d2f7d2: function(arg0, arg1, arg2) {
            arg0.title = getStringFromWasm0(arg1, arg2);
        },
        __wbg_set_valueAsNumber_952526c84deab0cc: function(arg0, arg1) {
            arg0.valueAsNumber = arg1;
        },
        __wbg_shiftKey_9bcb8bdd60c2f152: function(arg0) {
            const ret = arg0.shiftKey;
            return ret;
        },
        __wbg_stack_3b0d974bbf31e44f: function(arg0, arg1) {
            const ret = arg1.stack;
            const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg_startContainer_26afe9fe55f4aa15: function() { return handleError(function (arg0) {
            const ret = arg0.startContainer;
            return ret;
        }, arguments); },
        __wbg_startOffset_fb27b296ad8c85a8: function() { return handleError(function (arg0) {
            const ret = arg0.startOffset;
            return ret;
        }, arguments); },
        __wbg_static_accessor_GLOBAL_4ef717fb391d88b7: function() {
            const ret = typeof global === 'undefined' ? null : global;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_static_accessor_GLOBAL_THIS_8d1badc68b5a74f4: function() {
            const ret = typeof globalThis === 'undefined' ? null : globalThis;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_static_accessor_SELF_146583524fe1469b: function() {
            const ret = typeof self === 'undefined' ? null : self;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_static_accessor_WINDOW_f2829a2234d7819e: function() {
            const ret = typeof window === 'undefined' ? null : window;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_status_c45b3b9b3033184a: function(arg0) {
            const ret = arg0.status;
            return ret;
        },
        __wbg_stopPropagation_4c4ff88c29f9bc38: function(arg0) {
            arg0.stopPropagation();
        },
        __wbg_target_e759594a8d965ed7: function(arg0) {
            const ret = arg0.target;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_text_d3a29f7525a132c3: function() { return handleError(function (arg0) {
            const ret = arg0.text();
            return ret;
        }, arguments); },
        __wbg_then_16d107c451e9905d: function(arg0, arg1, arg2) {
            const ret = arg0.then(arg1, arg2);
            return ret;
        },
        __wbg_then_6ec10ae38b3e92f7: function(arg0, arg1) {
            const ret = arg0.then(arg1);
            return ret;
        },
        __wbg_valueAsNumber_b6bdc76edfdb9ea1: function(arg0) {
            const ret = arg0.valueAsNumber;
            return ret;
        },
        __wbg_value_1f687dfa7d6c3d08: function(arg0, arg1) {
            const ret = arg1.value;
            const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg_width_84477c442af415ce: function(arg0) {
            const ret = arg0.width;
            return ret;
        },
        __wbg_writeText_34bfead2ae78e5bb: function(arg0, arg1, arg2) {
            const ret = arg0.writeText(getStringFromWasm0(arg1, arg2));
            return ret;
        },
        __wbindgen_cast_0000000000000001: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [Externref], shim_idx: 3367, ret: Result(Unit), inner_ret: Some(Result(Unit)) }, mutable: true }) -> Externref`.
            const ret = makeMutClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___wasm_bindgen_41f5f8cae26fe08___JsValue__core_37ee0ce0c4cd57d5___result__Result_____wasm_bindgen_41f5f8cae26fe08___JsError___true_);
            return ret;
        },
        __wbindgen_cast_0000000000000002: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [F32, U32], shim_idx: 73, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___f32__u32______true_);
            return ret;
        },
        __wbindgen_cast_0000000000000003: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [F64, F64, F64, F64], shim_idx: 69, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___f64__f64__f64__f64______true_);
            return ret;
        },
        __wbindgen_cast_0000000000000004: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [F64, F64], shim_idx: 67, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___f64__f64______true_);
            return ret;
        },
        __wbindgen_cast_0000000000000005: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [F64, U32], shim_idx: 71, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___f64__u32______true_);
            return ret;
        },
        __wbindgen_cast_0000000000000006: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [F64], shim_idx: 65, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___f64______true_);
            return ret;
        },
        __wbindgen_cast_0000000000000007: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [I32, I32, I32], shim_idx: 75, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___i32__i32__i32______true_);
            return ret;
        },
        __wbindgen_cast_0000000000000008: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [I32, U32], shim_idx: 77, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___i32__u32______true_);
            return ret;
        },
        __wbindgen_cast_0000000000000009: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [I64, U32], shim_idx: 82, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___i64__u32______true_);
            return ret;
        },
        __wbindgen_cast_000000000000000a: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [NamedExternref("BeforeUnloadEvent")], shim_idx: 60, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_InputEvent__InputEvent______true_);
            return ret;
        },
        __wbindgen_cast_000000000000000b: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [NamedExternref("Event")], shim_idx: 86, ret: Unit, inner_ret: Some(Unit) }, mutable: true }) -> Externref`.
            const ret = makeMutClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_Event__Event______true_);
            return ret;
        },
        __wbindgen_cast_000000000000000c: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [NamedExternref("InputEvent")], shim_idx: 60, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_InputEvent__InputEvent______true__11);
            return ret;
        },
        __wbindgen_cast_000000000000000d: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [NamedExternref("KeyboardEvent")], shim_idx: 60, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_InputEvent__InputEvent______true__12);
            return ret;
        },
        __wbindgen_cast_000000000000000e: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [NamedExternref("MouseEvent")], shim_idx: 60, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_InputEvent__InputEvent______true__13);
            return ret;
        },
        __wbindgen_cast_000000000000000f: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [U32], shim_idx: 60, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_InputEvent__InputEvent______true__14);
            return ret;
        },
        __wbindgen_cast_0000000000000010: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [U32], shim_idx: 79, ret: Boolean, inner_ret: Some(Boolean) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___u32__bool__true_);
            return ret;
        },
        __wbindgen_cast_0000000000000011: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [], shim_idx: 84, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke_______true_);
            return ret;
        },
        __wbindgen_cast_0000000000000012: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [], shim_idx: 88, ret: Unit, inner_ret: Some(Unit) }, mutable: true }) -> Externref`.
            const ret = makeMutClosure(arg0, arg1, wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke_______true__1_);
            return ret;
        },
        __wbindgen_cast_0000000000000013: function(arg0) {
            // Cast intrinsic for `F64 -> Externref`.
            const ret = arg0;
            return ret;
        },
        __wbindgen_cast_0000000000000014: function(arg0) {
            // Cast intrinsic for `I64 -> Externref`.
            const ret = arg0;
            return ret;
        },
        __wbindgen_cast_0000000000000015: function(arg0, arg1) {
            // Cast intrinsic for `Ref(String) -> Externref`.
            const ret = getStringFromWasm0(arg0, arg1);
            return ret;
        },
        __wbindgen_init_externref_table: function() {
            const table = wasm.__wbindgen_externrefs;
            const offset = table.grow(4);
            table.set(0, undefined);
            table.set(offset + 0, undefined);
            table.set(offset + 1, null);
            table.set(offset + 2, true);
            table.set(offset + 3, false);
        },
    };
    return {
        __proto__: null,
        "./codillon_bg.js": import0,
    };
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke_______true_(arg0, arg1) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke_______true_(arg0, arg1);
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke_______true__1_(arg0, arg1) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke_______true__1_(arg0, arg1);
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_InputEvent__InputEvent______true_(arg0, arg1, arg2) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_InputEvent__InputEvent______true_(arg0, arg1, arg2);
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_Event__Event______true_(arg0, arg1, arg2) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_Event__Event______true_(arg0, arg1, arg2);
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_InputEvent__InputEvent______true__11(arg0, arg1, arg2) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_InputEvent__InputEvent______true__11(arg0, arg1, arg2);
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_InputEvent__InputEvent______true__12(arg0, arg1, arg2) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_InputEvent__InputEvent______true__12(arg0, arg1, arg2);
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_InputEvent__InputEvent______true__13(arg0, arg1, arg2) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_InputEvent__InputEvent______true__13(arg0, arg1, arg2);
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___wasm_bindgen_41f5f8cae26fe08___JsValue__core_37ee0ce0c4cd57d5___result__Result_____wasm_bindgen_41f5f8cae26fe08___JsError___true_(arg0, arg1, arg2) {
    const ret = wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___wasm_bindgen_41f5f8cae26fe08___JsValue__core_37ee0ce0c4cd57d5___result__Result_____wasm_bindgen_41f5f8cae26fe08___JsError___true_(arg0, arg1, arg2);
    if (ret[1]) {
        throw takeFromExternrefTable0(ret[0]);
    }
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___i64__u32______true_(arg0, arg1, arg2, arg3) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___i64__u32______true_(arg0, arg1, arg2, arg3);
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_InputEvent__InputEvent______true__14(arg0, arg1, arg2) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___web_sys_16a6c13be6ce63a6___features__gen_InputEvent__InputEvent______true__14(arg0, arg1, arg2);
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___u32__bool__true_(arg0, arg1, arg2) {
    const ret = wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___u32__bool__true_(arg0, arg1, arg2);
    return ret !== 0;
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___i32__u32______true_(arg0, arg1, arg2, arg3) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___i32__u32______true_(arg0, arg1, arg2, arg3);
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___i32__i32__i32______true_(arg0, arg1, arg2, arg3, arg4) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___i32__i32__i32______true_(arg0, arg1, arg2, arg3, arg4);
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___f64______true_(arg0, arg1, arg2) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___f64______true_(arg0, arg1, arg2);
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___f64__u32______true_(arg0, arg1, arg2, arg3) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___f64__u32______true_(arg0, arg1, arg2, arg3);
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___f64__f64______true_(arg0, arg1, arg2, arg3) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___f64__f64______true_(arg0, arg1, arg2, arg3);
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___f64__f64__f64__f64______true_(arg0, arg1, arg2, arg3, arg4, arg5) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___f64__f64__f64__f64______true_(arg0, arg1, arg2, arg3, arg4, arg5);
}

function wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___f32__u32______true_(arg0, arg1, arg2, arg3) {
    wasm.wasm_bindgen_41f5f8cae26fe08___convert__closures_____invoke___f32__u32______true_(arg0, arg1, arg2, arg3);
}


const __wbindgen_enum_ScrollBehavior = ["auto", "instant", "smooth"];


const __wbindgen_enum_ScrollLogicalPosition = ["start", "center", "end", "nearest"];

function addToExternrefTable0(obj) {
    const idx = wasm.__externref_table_alloc();
    wasm.__wbindgen_externrefs.set(idx, obj);
    return idx;
}

const CLOSURE_DTORS = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(state => wasm.__wbindgen_destroy_closure(state.a, state.b));

function debugString(val) {
    // primitive types
    const type = typeof val;
    if (type == 'number' || type == 'boolean' || val == null) {
        return  `${val}`;
    }
    if (type == 'string') {
        return `"${val}"`;
    }
    if (type == 'symbol') {
        const description = val.description;
        if (description == null) {
            return 'Symbol';
        } else {
            return `Symbol(${description})`;
        }
    }
    if (type == 'function') {
        const name = val.name;
        if (typeof name == 'string' && name.length > 0) {
            return `Function(${name})`;
        } else {
            return 'Function';
        }
    }
    // objects
    if (Array.isArray(val)) {
        const length = val.length;
        let debug = '[';
        if (length > 0) {
            debug += debugString(val[0]);
        }
        for(let i = 1; i < length; i++) {
            debug += ', ' + debugString(val[i]);
        }
        debug += ']';
        return debug;
    }
    // Test for built-in
    const builtInMatches = /\[object ([^\]]+)\]/.exec(toString.call(val));
    let className;
    if (builtInMatches && builtInMatches.length > 1) {
        className = builtInMatches[1];
    } else {
        // Failed to match the standard '[object ClassName]'
        return toString.call(val);
    }
    if (className == 'Object') {
        // we're a user defined class or Object
        // JSON.stringify avoids problems with cycles, and is generally much
        // easier than looping through ownProperties of `val`.
        try {
            return 'Object(' + JSON.stringify(val) + ')';
        } catch (_) {
            return 'Object';
        }
    }
    // errors
    if (val instanceof Error) {
        return `${val.name}: ${val.message}\n${val.stack}`;
    }
    // TODO we could test for more things here, like `Set`s and `Map`s.
    return className;
}

function getArrayU8FromWasm0(ptr, len) {
    ptr = ptr >>> 0;
    return getUint8ArrayMemory0().subarray(ptr / 1, ptr / 1 + len);
}

let cachedDataViewMemory0 = null;
function getDataViewMemory0() {
    if (cachedDataViewMemory0 === null || cachedDataViewMemory0.buffer.detached === true || (cachedDataViewMemory0.buffer.detached === undefined && cachedDataViewMemory0.buffer !== wasm.memory.buffer)) {
        cachedDataViewMemory0 = new DataView(wasm.memory.buffer);
    }
    return cachedDataViewMemory0;
}

function getStringFromWasm0(ptr, len) {
    return decodeText(ptr >>> 0, len);
}

let cachedUint8ArrayMemory0 = null;
function getUint8ArrayMemory0() {
    if (cachedUint8ArrayMemory0 === null || cachedUint8ArrayMemory0.byteLength === 0) {
        cachedUint8ArrayMemory0 = new Uint8Array(wasm.memory.buffer);
    }
    return cachedUint8ArrayMemory0;
}

function handleError(f, args) {
    try {
        return f.apply(this, args);
    } catch (e) {
        const idx = addToExternrefTable0(e);
        wasm.__wbindgen_exn_store(idx);
    }
}

function isLikeNone(x) {
    return x === undefined || x === null;
}

function makeClosure(arg0, arg1, f) {
    const state = { a: arg0, b: arg1, cnt: 1 };
    const real = (...args) => {

        // First up with a closure we increment the internal reference
        // count. This ensures that the Rust closure environment won't
        // be deallocated while we're invoking it.
        state.cnt++;
        try {
            return f(state.a, state.b, ...args);
        } finally {
            real._wbg_cb_unref();
        }
    };
    real._wbg_cb_unref = () => {
        if (--state.cnt === 0) {
            wasm.__wbindgen_destroy_closure(state.a, state.b);
            state.a = 0;
            CLOSURE_DTORS.unregister(state);
        }
    };
    CLOSURE_DTORS.register(real, state, state);
    return real;
}

function makeMutClosure(arg0, arg1, f) {
    const state = { a: arg0, b: arg1, cnt: 1 };
    const real = (...args) => {

        // First up with a closure we increment the internal reference
        // count. This ensures that the Rust closure environment won't
        // be deallocated while we're invoking it.
        state.cnt++;
        const a = state.a;
        state.a = 0;
        try {
            return f(a, state.b, ...args);
        } finally {
            state.a = a;
            real._wbg_cb_unref();
        }
    };
    real._wbg_cb_unref = () => {
        if (--state.cnt === 0) {
            wasm.__wbindgen_destroy_closure(state.a, state.b);
            state.a = 0;
            CLOSURE_DTORS.unregister(state);
        }
    };
    CLOSURE_DTORS.register(real, state, state);
    return real;
}

function passStringToWasm0(arg, malloc, realloc) {
    if (realloc === undefined) {
        const buf = cachedTextEncoder.encode(arg);
        const ptr = malloc(buf.length, 1) >>> 0;
        getUint8ArrayMemory0().subarray(ptr, ptr + buf.length).set(buf);
        WASM_VECTOR_LEN = buf.length;
        return ptr;
    }

    let len = arg.length;
    let ptr = malloc(len, 1) >>> 0;

    const mem = getUint8ArrayMemory0();

    let offset = 0;

    for (; offset < len; offset++) {
        const code = arg.charCodeAt(offset);
        if (code > 0x7F) break;
        mem[ptr + offset] = code;
    }
    if (offset !== len) {
        if (offset !== 0) {
            arg = arg.slice(offset);
        }
        ptr = realloc(ptr, len, len = offset + arg.length * 3, 1) >>> 0;
        const view = getUint8ArrayMemory0().subarray(ptr + offset, ptr + len);
        const ret = cachedTextEncoder.encodeInto(arg, view);

        offset += ret.written;
        ptr = realloc(ptr, len, offset, 1) >>> 0;
    }

    WASM_VECTOR_LEN = offset;
    return ptr;
}

function takeFromExternrefTable0(idx) {
    const value = wasm.__wbindgen_externrefs.get(idx);
    wasm.__externref_table_dealloc(idx);
    return value;
}

let cachedTextDecoder = new TextDecoder('utf-8', { ignoreBOM: true, fatal: true });
cachedTextDecoder.decode();
const MAX_SAFARI_DECODE_BYTES = 2146435072;
let numBytesDecoded = 0;
function decodeText(ptr, len) {
    numBytesDecoded += len;
    if (numBytesDecoded >= MAX_SAFARI_DECODE_BYTES) {
        cachedTextDecoder = new TextDecoder('utf-8', { ignoreBOM: true, fatal: true });
        cachedTextDecoder.decode();
        numBytesDecoded = len;
    }
    return cachedTextDecoder.decode(getUint8ArrayMemory0().subarray(ptr, ptr + len));
}

const cachedTextEncoder = new TextEncoder();

if (!('encodeInto' in cachedTextEncoder)) {
    cachedTextEncoder.encodeInto = function (arg, view) {
        const buf = cachedTextEncoder.encode(arg);
        view.set(buf);
        return {
            read: arg.length,
            written: buf.length
        };
    };
}

let WASM_VECTOR_LEN = 0;

let wasmModule, wasmInstance, wasm;
function __wbg_finalize_init(instance, module) {
    wasmInstance = instance;
    wasm = instance.exports;
    wasmModule = module;
    cachedDataViewMemory0 = null;
    cachedUint8ArrayMemory0 = null;
    wasm.__wbindgen_start();
    return wasm;
}

async function __wbg_load(module, imports) {
    if (typeof Response === 'function' && module instanceof Response) {
        if (typeof WebAssembly.instantiateStreaming === 'function') {
            try {
                return await WebAssembly.instantiateStreaming(module, imports);
            } catch (e) {
                const validResponse = module.ok && expectedResponseType(module.type);

                if (validResponse && module.headers.get('Content-Type') !== 'application/wasm') {
                    console.warn("`WebAssembly.instantiateStreaming` failed because your server does not serve Wasm with `application/wasm` MIME type. Falling back to `WebAssembly.instantiate` which is slower. Original error:\n", e);

                } else { throw e; }
            }
        }

        const bytes = await module.arrayBuffer();
        return await WebAssembly.instantiate(bytes, imports);
    } else {
        const instance = await WebAssembly.instantiate(module, imports);

        if (instance instanceof WebAssembly.Instance) {
            return { instance, module };
        } else {
            return instance;
        }
    }

    function expectedResponseType(type) {
        switch (type) {
            case 'basic': case 'cors': case 'default': return true;
        }
        return false;
    }
}

function initSync(module) {
    if (wasm !== undefined) return wasm;


    if (module !== undefined) {
        if (Object.getPrototypeOf(module) === Object.prototype) {
            ({module} = module)
        } else {
            console.warn('using deprecated parameters for `initSync()`; pass a single object instead')
        }
    }

    const imports = __wbg_get_imports();
    if (!(module instanceof WebAssembly.Module)) {
        module = new WebAssembly.Module(module);
    }
    const instance = new WebAssembly.Instance(module, imports);
    return __wbg_finalize_init(instance, module);
}

async function __wbg_init(module_or_path) {
    if (wasm !== undefined) return wasm;


    if (module_or_path !== undefined) {
        if (Object.getPrototypeOf(module_or_path) === Object.prototype) {
            ({module_or_path} = module_or_path)
        } else {
            console.warn('using deprecated parameters for the initialization function; pass a single object instead')
        }
    }

    if (module_or_path === undefined) {
        module_or_path = new URL('codillon_bg.wasm', import.meta.url);
    }
    const imports = __wbg_get_imports();

    if (typeof module_or_path === 'string' || (typeof Request === 'function' && module_or_path instanceof Request) || (typeof URL === 'function' && module_or_path instanceof URL)) {
        module_or_path = fetch(module_or_path);
    }

    const { instance, module } = await __wbg_load(await module_or_path, imports);

    return __wbg_finalize_init(instance, module);
}

export { initSync, __wbg_init as default };
