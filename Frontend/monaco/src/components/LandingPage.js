import React, { useEffect, useState } from "react";
import CodeEditorWindow from "./EditorWindow";
import axios from "axios";
import { classnames } from "../utils/generalSpecs";
import { languageOptions } from "../constants/languageYAPL";

import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import { defineTheme } from "../lib/defineTheme";
import useKeyPress from "../hooks/useKeyPressed";
import Footer from "./FooterSpace";
import OutputWindow from "./OutputWin";
import CustomInput from "./Input";
import OutputDetails from "./Details";
import ThemeDropdown from "./Theme";
import LanguagesDropdown from "./Dropdown";

const javascriptDefault = `class Main inherits IO {
  main(): SELF_TYPE {
 out_string("Hello, World.\n")
  };
};
`;

const Landing = () => {
  const [code, setCode] = useState(javascriptDefault);
  const [customInput, setCustomInput] = useState("");
  const [outputDetails, setOutputDetails] = useState(null);
  const [processing, setProcessing] = useState(null);
  const [theme, setTheme] = useState("cobalt");
  const [language, setLanguage] = useState(languageOptions[0]);

  const enterPress = useKeyPress("Enter");
  const ctrlPress = useKeyPress("Control");

  const onSelectChange = (sl) => {
    console.log("selected Option...", sl);
    setLanguage(sl);
  };

  useEffect(() => {
    if (enterPress && ctrlPress) {
      console.log("enterPress", enterPress);
      console.log("ctrlPress", ctrlPress);
      handleCompile();
    }
  }, [ctrlPress, enterPress]);
  const onChange = (action, data) => {
    switch (action) {
      case "code": {
        setCode(data);
        break;
      }
      default: {
        console.warn("case not handled!", action, data);
      }
    }
  };

  /**
   * @TODO this function has to change to use our API from flask
   */
  const handleCompile = () => {
    setProcessing(true);
    showSuccessToast("Compiled Successfully!");
    axios.post("http://localhost:5000/yapl_compile", {
      code: code,
      language: language.value,
    },{
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    }).then((res) => {
      setOutputDetails(res.data);
      setProcessing(false);
    }).catch((err) => {
      console.log("err", err);
      showErrorToast();
      setProcessing(false);
    });
    setOutputDetails(null);
    setProcessing(false);
    // const data = {
    //   language_id: language.id,
    //   // encode source code in base64
    //   source_code: btoa(code),
    //   stdin: btoa(customInput),
    // };
    // const options = {
    //   method: "POST",
    //   url: process.env.REACT_APP_RAPID_API_URL,
    //   params: { base64_encoded: "true", fields: "*" },
    //   headers: {
    //     "content-type": "application/json",
    //     "Content-Type": "application/json",
    //   },
    //   data,
    // };

    // axios
    //   .request(options)
    //   .then(function (response) {
    //     console.log("res.data", response.data);
    //   })
    //   .catch((err) => {
    //     let error = err.response ? err.response.data : err;
    //     // get error status
    //     let status = err.response.status;
    //     console.log("status", status);
    //     if (status === 429) {
    //       console.log("too many requests", status);

    //       showErrorToast(
    //         `Quota of 100 requests exceeded for the Day! Please read the blog on freeCodeCamp to learn how to setup your own RAPID API Judge0!`,
    //         10000
    //       );
    //     }
    //     setProcessing(false);
    //     console.log("catch block...", error);
    //   });
  };


  function handleThemeChange(th) {
    const theme = th;
    console.log("theme...", theme);

    if (["light", "vs-dark"].includes(theme.value)) {
      setTheme(theme);
    } else {
      defineTheme(theme.value).then((_) => setTheme(theme));
    }
  }
  useEffect(() => {
    defineTheme("oceanic-next").then((_) =>
      setTheme({ value: "oceanic-next", label: "Oceanic Next" })
    );
  }, []);

  const showSuccessToast = (msg) => {
    toast.success(msg || `Compiled Successfully!`, {
      position: "top-right",
      autoClose: 1000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      progress: undefined,
    });
  };
  const showErrorToast = (msg, timer) => {
    toast.error(msg || `Something went wrong! Please try again.`, {
      position: "top-right",
      autoClose: timer ? timer : 1000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      progress: undefined,
    });
  };

  return (
    <>
      <ToastContainer
        position="top-right"
        autoClose={2000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />

      <div className="h-4 w-full bg-gradient-to-r from-pink-500 via-red-500 to-yellow-500"></div>
      <div className="flex flex-row">
        <div className="px-4 py-2">
          <LanguagesDropdown onSelectChange={onSelectChange} />
        </div>
        <div className="px-4 py-2">
          <ThemeDropdown handleThemeChange={handleThemeChange} theme={theme} />
        </div>
      </div>
      <div className="flex flex-row space-x-4 items-start px-4 py-4">
        <div className="flex flex-col w-full h-full justify-start items-start">
          <CodeEditorWindow
            code={code}
            onChange={onChange}
            language={language?.value}
            theme={theme.value}
          />
          <h1 className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700 mb-2">Three Address Code </h1>
          <CodeEditorWindow
            code={code}
            language={"txt"}
            theme={theme.value}
          />
        </div>

        <div className="right-container flex flex-shrink-0 w-[30%] flex-col">
          <OutputWindow outputDetails={outputDetails} />
          <div className="flex flex-col items-end">
            <CustomInput
              customInput={customInput}
              setCustomInput={setCustomInput}
            />
            <button
              onClick={handleCompile}
              disabled={!code}
              className={classnames(
                "mt-4 border-2 border-black z-10 rounded-md shadow-[5px_5px_0px_0px_rgba(0,0,0)] px-4 py-2 hover:shadow transition duration-200 bg-white flex-shrink-0",
                !code ? "opacity-50" : ""
              )}
            >
              {processing ? "Processing..." : "Compile and Execute"}
            </button>
          </div>
          {outputDetails && <OutputDetails outputDetails={outputDetails} />}
        </div>
      </div>
      <Footer />
    </>
  );
};
export default Landing;