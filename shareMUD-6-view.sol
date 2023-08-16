//SPDX-License-Identifier: UNLICENSED
pragma solidity >= 0.8.18;

import './shareMUD-6.sol';

contract viewFunctions is MUDsharing {

    function viewOpenRequests() view public returns(single_request[] memory){
        return viewRequests;
    }
    function viewOfferList(bytes32 _uniqueID) view public returns(single_offer[] memory) {
        return OfferList[_uniqueID];
    }
    function view_submission(bytes32 _uniqueID) view public returns(single_submission[] memory) {
        return(submissionList[_uniqueID]);
    }
    function ViewRate(address _supplierAddr) view public returns(single_rate[] memory) {
        return(rateList[_supplierAddr]);
    }
}