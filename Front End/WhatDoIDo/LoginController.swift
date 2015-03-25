//
//  LoginController.swift
//  WhatDoIDo
//
//  Created by CSSE Department on 9/25/14.
//  Copyright (c) 2014 PaJamaKinG. All rights reserved.2
//

import Foundation
import UIKit

class LoginController: UIViewController, UITextFieldDelegate {
    
    @IBOutlet var uNameField : UITextField! //uNameField.text
    @IBOutlet var passwordField : UITextField! //passwordField.text
    @IBOutlet var loginButton : UIButton!
    
    var del = UIApplication.sharedApplication().delegate as AppDelegate
    
    @IBAction func login(sender: AnyObject) {
        if (uNameField.text != "bypass") {
        del.user.login(["username":uNameField.text, "password":passwordField.text], url: "http://whatdoido.csse.rose-hulman.edu/api/login") { (succeeded: Bool, msg: String, token: String) -> () in
            var alert = UIAlertView(title: "Success!", message: msg, delegate: nil, cancelButtonTitle: "Okay.")
            if(succeeded) {
                self.del.user.changeName(self.uNameField.text)
                self.del.user.changePassword(self.passwordField.text)
                self.del.user.postSuccess()
                self.del.user.setLoginToken(token)
                alert.title = "Success!"
                alert.message = msg
            }
            else {
                self.del.user.postFailure()
                alert.title = "Failed"
                alert.message = msg
            }
            println(succeeded)
            // Move to the UI thread
            dispatch_async(dispatch_get_main_queue(), { () -> Void in
                // Show the alert
                if (!succeeded) {
                    alert.show()
                }
                if (self.del.user.wasLoginSuccessful()) {
                    self.performLoginSegue()
                }
            })
            } }
        else {
            self.performLoginSegue();
        }
    }
    
    func performLoginSegue() {
        performSegueWithIdentifier("login", sender: self);
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        uNameField.delegate = self
        passwordField.delegate = self
        // Do any additional setup after loading the view, typically from a nib.
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject!) {

    }
    
    func textFieldShouldReturn(textField: UITextField!) -> Bool // called when 'return' key pressed. return NO to ignore.
    {
        textField.resignFirstResponder()
        return true;
    }
    
}