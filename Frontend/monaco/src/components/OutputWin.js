import React from "react";

const OutputWindow = ({ outputDetails }) => {
  const getOutput = () => {
    //Show green if result array is empty and red if not
    return (
      <>
        <div className="flex flex-col">
          <div className="flex flex-row justify-between items-center px-4 py-2">
            <h1 className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700">
              Result
            </h1>
            <div
              className={`w-4 h-4 rounded-full ${
                outputDetails.result.length === 0
                  ? "bg-green-500"
                  : "bg-red-500"
              }`}
            ></div>
          </div>
          <div className="flex flex-col px-4 py-2">
          {outputDetails.result.length === 0 ? (
              <p className="text-white">No errors found</p>
            ) : outputDetails.result.map((item, index) => (
              <div key={index} className="flex flex-row">
                <div className="w-4 h-4 rounded-full bg-gray-500 mr-2"></div>
                <p className="text-white">{item}</p>
              </div>
            ))}
          </div>
        </div>
      </>
    );

  };
  return (
    <>
      <h1 className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700 mb-2">
        Output
      </h1>
      <div className="w-full h-56 bg-[#1e293b] rounded-md text-white font-normal text-sm overflow-y-auto">
        {outputDetails ? <>{getOutput()}</> : null}
      </div>
    </>
  );
};

export default OutputWindow;