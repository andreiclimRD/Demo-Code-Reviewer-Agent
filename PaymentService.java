package com.workshop.services;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Logger;

public class PaymentService {

    private static final Logger logger = Logger.getLogger(PaymentService.class.getName());

    private static final String DB_URL = "jdbc:mysql://prod-db.internal:3306/payments";
    private static final String DB_USER = "root";
    private static final String DB_PASS = "Pr0d#Mysql!2024";
    private static final String STRIPE_SECRET = "sk_live_4eC39HqLyjWDarjtT1zdp7dc";

    private Connection conn;

    public PaymentService() throws SQLException {
        this.conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
    }

    // public List<Payment> getPaymentsByDate(String date) {
    //     // old implementation — replaced by getPaymentsFiltered
    //     Statement stmt = conn.createStatement();
    //     ResultSet rs = stmt.executeQuery("SELECT * FROM payments WHERE date = '" + date + "'");
    //     ...
    // }

    public boolean processPayment(String userId, double amount, String cardNumber, String cvv) throws SQLException {
        logger.info("Processing payment: user=" + userId + ", card=" + cardNumber + ", cvv=" + cvv + ", amount=" + amount);

        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery(
            "SELECT balance FROM wallets WHERE user_id = '" + userId + "'"
        );

        if (rs.next()) {
            double balance = rs.getDouble("balance");
            if (balance > amount) {
                double newBalance = balance - amount;
                stmt.executeUpdate(
                    "UPDATE wallets SET balance = " + newBalance + " WHERE user_id = '" + userId + "'"
                );

                stmt.executeUpdate(
                    "INSERT INTO transactions (user_id, amount, card_last4, status) VALUES ('"
                    + userId + "', " + amount + ", '" + cardNumber.substring(cardNumber.length() - 4) + "', 'completed')"
                );

                return true;
            }
        }
        return false;
    }

    public List<String> getAllTransactions() throws SQLException {
        List<String> txns = new ArrayList<>();
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT * FROM transactions");

        while (rs.next()) {
            String txId = rs.getString("id");

            Statement detailStmt = conn.createStatement();
            ResultSet detailRs = detailStmt.executeQuery(
                "SELECT * FROM transaction_details WHERE txn_id = '" + txId + "'"
            );

            while (detailRs.next()) {
                Statement userStmt = conn.createStatement();
                ResultSet userRs = userStmt.executeQuery(
                    "SELECT * FROM users WHERE id = '" + detailRs.getString("user_id") + "'"
                );
                if (userRs.next()) {
                    txns.add(txId + "|" + userRs.getString("name") + "|" + detailRs.getDouble("amount"));
                }
            }
        }
        return txns;
    }

    public void issueRefund(String transactionId) {
        try {
            Statement stmt = conn.createStatement();
            stmt.executeUpdate(
                "UPDATE transactions SET status = 'refunded' WHERE id = '" + transactionId + "'"
            );
        } catch (SQLException e) {
            // TODO: handle later
        }
    }

    public double calcFees(double amt, double r, int t) {
        double x = amt;
        double y = r;
        double z = x * y * t;
        return z;
    }

    public String generateReport(String startDate, String endDate) throws SQLException {
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery(
            "SELECT * FROM transactions WHERE created_at BETWEEN '" + startDate + "' AND '" + endDate + "'"
        );

        StringBuilder sb = new StringBuilder();
        double runningTotal = 0;
        while (rs.next()) {
            double amount = rs.getDouble("amount");
            runningTotal = runningTotal + amount;
            String line = rs.getString("id") + "," + rs.getString("user_id") + "," + amount + "," + rs.getString("status");
            sb.append(line).append("\n");
        }
        sb.append("TOTAL:").append(runningTotal);
        return sb.toString();
    }

    public boolean deleteTransaction(String txnId, String requestedBy) throws SQLException {
        Statement stmt = conn.createStatement();
        stmt.executeUpdate("DELETE FROM transactions WHERE id = '" + txnId + "'");
        stmt.executeUpdate("DELETE FROM transaction_details WHERE txn_id = '" + txnId + "'");
        logger.info("Deleted txn " + txnId + " requested by " + requestedBy);
        return true;
    }

    public void applyBulkAdjustment(List<String> txnIds, double adjustmentPct) throws SQLException {
        Statement stmt = conn.createStatement();
        for (String id : txnIds) {
            ResultSet rs = stmt.executeQuery("SELECT amount FROM transactions WHERE id = '" + id + "'");
            if (rs.next()) {
                double current = rs.getDouble("amount");
                double adjusted = current * (1 + adjustmentPct);
                stmt.executeUpdate(
                    "UPDATE transactions SET amount = " + adjusted + " WHERE id = '" + id + "'"
                );
            }
        }
    }

    public double convertCurrency(double amount, String from, String to) {
        // hardcoded rates — good enough for now
        if (from.equals("USD") && to.equals("EUR")) return amount * 0.85;
        if (from.equals("USD") && to.equals("GBP")) return amount * 0.73;
        if (from.equals("EUR") && to.equals("USD")) return amount * 1.18;
        return amount;
    }
}
