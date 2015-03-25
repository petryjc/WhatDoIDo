//
//  SettingsViewController.swift
//  WhatDoIDo
//
//  Created by CSSE Department on 10/19/14.
//  Copyright (c) 2014 PaJamaKinG. All rights reserved.
//

import Foundation
import UIKit
import CoreLocation

class SettingsViewController: UIViewController, UITableViewDelegate, UITableViewDataSource {
    
    @IBOutlet var uNameLabel : UILabel!
    @IBOutlet var refreshButton : UIButton!
    @IBOutlet var settingsTableView : UITableView!
    
    var del = UIApplication.sharedApplication().delegate as AppDelegate
    var loadedName: String!
    var settingsList = ["Interests", "Log-out", "Delete Account"]
    
    @IBAction func refresh() {
        self.refreshUI()
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.settingsTableView.registerClass(UITableViewCell.self, forCellReuseIdentifier: "cell")
        refreshUI()
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    func tableView(settingsTableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return settingsList.count //Set this number to the number of settings
    }
    
    func tableView(settingsTableView: UITableView, cellForRowAtIndexPath indexPath: NSIndexPath) -> UITableViewCell {
        var cell:UITableViewCell = self.settingsTableView.dequeueReusableCellWithIdentifier("cell") as UITableViewCell
        
        //var cell = UITableViewCell(style: UITableViewCellStyle.Value2, reuseIdentifier: nil);
        
        cell.textLabel.text = settingsList[indexPath.row]
        return cell
    }
    
    func tableView(settingsTableView: UITableView!, didSelectRowAtIndexPath indexPath: NSIndexPath!) {
        println(indexPath.row) //This is where you do something with the selected setting
        if (indexPath.row == 0) {
            performSegueWithIdentifier("interests", sender: self)
        } else if (indexPath.row == 1) {
            logout("test");
        } else if (indexPath.row == 2) {
            deleteAccount("test");
        }
    }
    
    @IBAction func logout(sender: AnyObject) {
        del.user.logout(["token": del.user.getLoginToken()], url: "http://whatdoido.csse.rose-hulman.edu/api/logout") { (succeeded: Bool, msg: String) -> () in
            dispatch_async(dispatch_get_main_queue(), { () -> Void in
                self.del.locationManager.stopUpdatingLocation()
                self.performLogoutSegue();
            })
        }
    }
    
    @IBAction func deleteAccount(sender: AnyObject) {
        del.user.deleteAccount(["username": del.user.getName(), "password": del.user.getPass()], url: "http://whatdoido.csse.rose-hulman.edu/api/deleteAccount") { (succeeded: Bool, msg: String) -> () in
            dispatch_async(dispatch_get_main_queue(), { () -> Void in
                self.del.locationManager.stopUpdatingLocation()
                self.performLogoutSegue();
            })
        }
    }
    
    func performLogoutSegue() {
        performSegueWithIdentifier("logout", sender: self);
    }
    
    func refreshUI() {

    }
    
}