// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VoteStorage {
    struct Vote {
        uint256 signature;
        uint256 randomNumber;
    }

    Vote[] public votes;

    function storeVote(uint256 _signature, uint256 _randomNumber) public {
        votes.push(Vote(_signature, _randomNumber));
    }

    function getVotesCount() public view returns (uint256) {
        return votes.length;
    }

    function getVote(uint256 index) public view returns (uint256, uint256) {
        Vote memory vote = votes[index];
        return (vote.signature, vote.randomNumber);
    }
}