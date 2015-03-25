//
//  SuggestionModel.swift
//  WhatDoIDo
//
//  Created by CSSE Department on 10/24/14.
//  Copyright (c) 2014 PaJamaKinG. All rights reserved.
//

import Foundation

class SuggestionModel {
    
    var name: String
    var description: String
    var route: String
    var location: String
    var contact: String
    var startTime: String
    var endTime: String
    
    init() {
        name = "Example Suggestion"
        description = "Suggestion Desc"
        route = "Suggestion Route"
        location = "Suggestion Location"
        contact = "Suggestion Contact"
        startTime = "Suggestion Time"
        endTime = "Boy I don't care"
    }
    
    func getName() -> String {
        return self.name
    }
    
    func getDesc() -> String {
        return self.description
    }
    
    func getRoute() -> String {
        return self.route
    }
    
    func getLocation() -> String {
        return self.location
    }
    
    func getContact() -> String {
        return self.contact
    }
    
    func getStartTime() -> String {
        return self.startTime
    }
    
    func getEndTime() -> String {
        return self.endTime
    }

    func setName(name: String) {
        self.name = name
    }
    
}